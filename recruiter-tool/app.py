from __future__ import annotations

import os
import sqlite3
import time
from contextlib import contextmanager
from functools import wraps

from flask import Flask, g, jsonify, make_response, render_template, request, send_file

from ai_processor import CandidateValidationError, extract_candidate_info, generate_candidate_brief
from database import DB_PATH, get_candidate, init_db, save_candidate, search_candidates
from file_handler import delete_attachment, get_attachments, init_upload_folder, save_attachment
from telemetry import new_pipeline_run_id, span, summarize_text, write_run_summary

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

init_db()
init_upload_folder()


def _merge_metrics(metrics: dict | None = None) -> None:
    if not metrics:
        return
    current = getattr(g, "run_metrics", {})
    current.update(metrics)
    g.run_metrics = current


def _merge_attrs(attrs: dict | None = None) -> None:
    if not attrs:
        return
    current = getattr(g, "run_attrs", {})
    current.update(attrs)
    g.run_attrs = current


def _mark_route_error(exc: Exception, *, http_status_code: int | None = None, metrics: dict | None = None) -> None:
    _merge_metrics(metrics)
    route_span = getattr(g, "route_span", None)
    if route_span is not None:
        route_span.set_error(exc, http_status_code=http_status_code)


@contextmanager
def _stage_span(name: str, category: str = "stage"):
    with span(
        name,
        category,
        g.pipeline_run_id,
        parent_span_id=getattr(g, "route_span_id", None),
        route=request.path,
    ) as stage_record:
        yield stage_record


def instrument_route(name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            pipeline_run_id = new_pipeline_run_id()
            request_started_ns = time.perf_counter_ns()
            request_body = request.get_data(cache=True) or b""

            g.pipeline_run_id = pipeline_run_id
            g.request_started_ns = request_started_ns
            g.run_metrics = {}
            g.run_attrs = {}

            with span(
                name,
                "http",
                pipeline_run_id,
                route=request.path,
                method=request.method,
            ) as route_span:
                g.route_span = route_span
                g.route_span_id = route_span.span_id
                route_span.set_metric("request_body_bytes", len(request_body))

                try:
                    response = make_response(func(*args, **kwargs))
                except Exception as exc:
                    route_span.set_error(exc, http_status_code=500)
                    response = make_response(jsonify({"error": "Internal server error"}), 500)

                run_wall_ms = round((time.perf_counter_ns() - request_started_ns) / 1_000_000, 3)
                route_span.update_attrs(getattr(g, "run_attrs", {}))
                route_span.update_metrics(getattr(g, "run_metrics", {}))
                route_span.set_metric("run.wall_ms", run_wall_ms)
                route_span.set_metric("http.status_code", response.status_code)
                route_span.set_metric("request.success", response.status_code < 400)
                route_span.set_status("ok" if response.status_code < 400 else "error")

                summary = {
                    "pipeline_run_id": pipeline_run_id,
                    "route": request.path,
                    "method": request.method,
                    "status": "ok" if response.status_code < 400 else "error",
                    "http_status_code": response.status_code,
                    "run.wall_ms": run_wall_ms,
                    **getattr(g, "run_attrs", {}),
                    **getattr(g, "run_metrics", {}),
                }
                write_run_summary(summary)

                response.headers["X-Pipeline-Run-Id"] = pipeline_run_id
                return response

        return wrapper

    return decorator


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
@instrument_route("http.process_candidate")
def process_transcript():
    try:
        with _stage_span("stage.request_parse") as parse_span:
            data = request.get_json() or {}
            transcript = data.get("transcript", "")
            search_tags = data.get("search_tags", [])

            parse_metrics = {
                **summarize_text("transcript", transcript),
                "search_tags_count": len(search_tags) if isinstance(search_tags, list) else 0,
            }
            parse_span.update_metrics(parse_metrics)
            _merge_metrics(parse_metrics)

            if not transcript:
                raise ValueError("No transcript provided")

        with _stage_span("stage.llm_extract") as llm_stage:
            candidate_data, extraction_metadata = extract_candidate_info(
                transcript,
                pipeline_run_id=g.pipeline_run_id,
                parent_span_id=llm_stage.span_id,
            )
            llm_metrics = {
                key: value
                for key, value in extraction_metadata.items()
                if key not in {"response_id", "model", "reasoning_effort", "fact_check_warnings"}
            }
            llm_stage.update_metrics(llm_metrics)
            if extraction_metadata.get("response_id"):
                llm_stage.set_attr("response_id", extraction_metadata["response_id"])
            _merge_metrics(llm_metrics)
            _merge_attrs(
                {
                    "response_id": extraction_metadata.get("response_id"),
                    "model": extraction_metadata.get("model"),
                    "reasoning_effort": extraction_metadata.get("reasoning_effort"),
                }
            )

        candidate_data["transcript"] = transcript
        candidate_data["search_tags"] = search_tags if isinstance(search_tags, list) else []

        with _stage_span("stage.brief_render") as brief_span:
            brief = generate_candidate_brief(candidate_data)
            brief_metrics = summarize_text("brief", brief)
            brief_metrics = {
                "brief_chars": brief_metrics["brief_chars"],
                "brief_bytes": brief_metrics["brief_bytes"],
            }
            brief_span.update_metrics(brief_metrics)
            _merge_metrics(brief_metrics)

        with _stage_span("stage.db_save") as db_span:
            candidate_id = save_candidate(candidate_data)
            db_span.set_metric("candidate_id", candidate_id)
            _merge_metrics({"candidate_id": candidate_id})
            _merge_attrs({"candidate_id": candidate_id})

        return jsonify(
            {
                "success": True,
                "candidate_id": candidate_id,
                "brief": brief,
                "data": candidate_data,
            }
        )

    except CandidateValidationError as exc:
        _mark_route_error(exc, http_status_code=500, metrics=exc.metrics)
        return jsonify({"error": str(exc)}), 500
    except ValueError as exc:
        _mark_route_error(exc, http_status_code=400)
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        _mark_route_error(exc, http_status_code=500)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/search", methods=["GET"])
@instrument_route("http.search_candidates")
def search():
    try:
        filters = {
            "therapeutic_area": request.args.get("therapeutic_area"),
            "phase": request.args.get("phase"),
            "company": request.args.get("company"),
            "search_tag": request.args.get("search_tag"),
            "days_back": request.args.get("days_back"),
        }
        filters = {k: v for k, v in filters.items() if v}

        candidates = search_candidates(filters)
        metrics = {"candidate_count": len(candidates), "filter_count": len(filters)}
        _merge_metrics(metrics)

        return jsonify({"success": True, "count": len(candidates), "candidates": candidates})

    except Exception as exc:
        _mark_route_error(exc, http_status_code=500)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/candidate/<int:candidate_id>", methods=["GET"])
@instrument_route("http.get_candidate")
def get_candidate_detail(candidate_id):
    try:
        candidate = get_candidate(candidate_id)
        _merge_attrs({"candidate_id": candidate_id})

        if not candidate:
            raise LookupError("Candidate not found")

        brief = generate_candidate_brief(candidate)
        _merge_metrics({"brief_chars": len(brief), "brief_bytes": len(brief.encode("utf-8"))})

        return jsonify({"success": True, "candidate": candidate, "brief": brief})

    except LookupError as exc:
        _mark_route_error(exc, http_status_code=404)
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        _mark_route_error(exc, http_status_code=500)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/export", methods=["POST"])
@instrument_route("http.export_candidates")
def export_candidates():
    try:
        data = request.get_json() or {}
        filters = data.get("filters", {})

        candidates = search_candidates(filters)
        export_text = ""
        for index, candidate in enumerate(candidates, 1):
            brief = generate_candidate_brief(candidate)
            export_text += f"\n{'=' * 80}\n"
            export_text += f"CANDIDATE #{index}\n"
            export_text += f"{'=' * 80}\n\n"
            export_text += brief
            export_text += "\n"

        _merge_metrics(
            {
                "candidate_count": len(candidates),
                "export_chars": len(export_text),
                "export_bytes": len(export_text.encode("utf-8")),
            }
        )

        return jsonify({"success": True, "count": len(candidates), "export_text": export_text})

    except Exception as exc:
        _mark_route_error(exc, http_status_code=500)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/candidate/<int:candidate_id>/upload", methods=["POST"])
@instrument_route("http.upload_attachment")
def upload_attachment(candidate_id):
    try:
        if "file" not in request.files:
            raise ValueError("No file provided")

        file = request.files["file"]
        description = request.form.get("description", "")
        _merge_attrs({"candidate_id": candidate_id})

        with _stage_span("stage.file_save", category="file") as file_span:
            attachment_id = save_attachment(candidate_id, file, description)
            file_metrics = {
                "file_size_bytes": getattr(file, "content_length", None) or 0,
                "file_mime_type": file.mimetype or "",
                "description_chars": len(description),
            }
            file_span.update_metrics(file_metrics)
            file_span.set_metric("attachment_id", attachment_id)
            _merge_metrics({**file_metrics, "attachment_id": attachment_id})

        return jsonify(
            {
                "success": True,
                "attachment_id": attachment_id,
                "message": "File uploaded successfully",
            }
        )

    except ValueError as exc:
        _mark_route_error(exc, http_status_code=400)
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        _mark_route_error(exc, http_status_code=500)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/candidate/<int:candidate_id>/attachments", methods=["GET"])
@instrument_route("http.get_attachments")
def get_candidate_attachments(candidate_id):
    try:
        _merge_attrs({"candidate_id": candidate_id})
        with _stage_span("stage.db_lookup", category="db") as db_span:
            attachments = get_attachments(candidate_id)
            db_span.set_metric("attachment_count", len(attachments))
            _merge_metrics({"attachment_count": len(attachments)})

        return jsonify({"success": True, "attachments": attachments})

    except Exception as exc:
        _mark_route_error(exc, http_status_code=500)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/attachment/<int:attachment_id>/download", methods=["GET"])
@instrument_route("http.download_attachment")
def download_attachment(attachment_id):
    try:
        _merge_attrs({"attachment_id": attachment_id})
        with _stage_span("stage.db_lookup", category="db") as db_span:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT file_path, file_name FROM attachments WHERE id = ?", (attachment_id,))
            row = cursor.fetchone()
            conn.close()
            db_span.set_metric("attachment_found", bool(row))

        if not row:
            raise LookupError("Attachment not found")

        file_path, file_name = row

        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found on disk")

        with _stage_span("stage.file_send", category="file") as file_span:
            file_size = os.path.getsize(file_path)
            file_span.update_metrics({"file_size_bytes": file_size})
            _merge_metrics({"file_size_bytes": file_size})

        return send_file(file_path, as_attachment=True, download_name=file_name)

    except LookupError as exc:
        _mark_route_error(exc, http_status_code=404)
        return jsonify({"error": str(exc)}), 404
    except FileNotFoundError as exc:
        _mark_route_error(exc, http_status_code=404)
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        _mark_route_error(exc, http_status_code=500)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/attachment/<int:attachment_id>", methods=["DELETE"])
@instrument_route("http.delete_attachment")
def remove_attachment(attachment_id):
    try:
        _merge_attrs({"attachment_id": attachment_id})
        with _stage_span("stage.file_delete", category="file"):
            delete_attachment(attachment_id)

        return jsonify({"success": True, "message": "Attachment deleted successfully"})

    except Exception as exc:
        _mark_route_error(exc, http_status_code=500)
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
