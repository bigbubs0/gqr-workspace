from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator


_LOCK = threading.Lock()
_BASE_DIR = Path(__file__).resolve().parent


def telemetry_enabled() -> bool:
    return os.getenv("TELEMETRY_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}


def telemetry_dir() -> Path:
    raw_dir = os.getenv("TELEMETRY_DIR", "telemetry").strip() or "telemetry"
    path = Path(raw_dir)
    if not path.is_absolute():
        path = _BASE_DIR / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def _file_path(name: str) -> Path:
    return telemetry_dir() / name


def _now_us() -> int:
    return time.time_ns() // 1_000


def _json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _safe_error_message(message: str | None) -> str:
    if not message:
        return ""
    sanitized = " ".join(str(message).split())
    return sanitized[:300]


def _append_ndjson(filename: str, payload: dict) -> None:
    if not telemetry_enabled():
        return

    path = _file_path(filename)
    with _LOCK, path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True, separators=(",", ":"), default=_json_default))
        handle.write("\n")


def new_pipeline_run_id() -> str:
    return f"run_{uuid.uuid4().hex[:20]}"


def sha256_text(value: str) -> str:
    return hashlib.sha256((value or "").encode("utf-8")).hexdigest()


def summarize_text(name: str, value: str | None) -> dict:
    value = value or ""
    encoded = value.encode("utf-8")
    return {
        f"{name}_sha256": sha256_text(value),
        f"{name}_chars": len(value),
        f"{name}_bytes": len(encoded),
        f"{name}_lines": value.count("\n") + (1 if value else 0),
    }


def summarize_bytes(name: str, value: bytes | None) -> dict:
    value = value or b""
    digest = hashlib.sha256(value).hexdigest()
    return {
        f"{name}_sha256": digest,
        f"{name}_bytes": len(value),
    }


def sanitize_error(error: Exception | dict | str | None, *, http_status_code: int | None = None) -> dict | None:
    if error is None:
        return None

    if isinstance(error, Exception):
        payload = {
            "type": type(error).__name__,
            "message": _safe_error_message(str(error)),
        }
    elif isinstance(error, dict):
        payload = {
            "type": str(error.get("type", "Error")),
            "message": _safe_error_message(str(error.get("message", ""))),
        }
        if error.get("http_status_code") is not None:
            payload["http_status_code"] = error["http_status_code"]
    else:
        payload = {
            "type": "Error",
            "message": _safe_error_message(str(error)),
        }

    if http_status_code is not None:
        payload["http_status_code"] = http_status_code

    return payload


@dataclass
class SpanRecord:
    name: str
    category: str
    pipeline_run_id: str
    parent_span_id: str | None = None
    attrs: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    start_us: int = field(default_factory=_now_us)
    _start_perf_ns: int = field(default_factory=time.perf_counter_ns)
    status: str = "ok"
    error: dict | None = None

    def set_attr(self, key: str, value: Any) -> None:
        self.attrs[key] = value

    def update_attrs(self, attrs: dict[str, Any] | None) -> None:
        if attrs:
            self.attrs.update(attrs)

    def set_metric(self, key: str, value: Any) -> None:
        self.metrics[key] = value

    def update_metrics(self, metrics: dict[str, Any] | None) -> None:
        if metrics:
            self.metrics.update(metrics)

    def set_status(self, status: str) -> None:
        self.status = status

    def set_error(self, error: Exception | dict | str, *, http_status_code: int | None = None) -> None:
        self.status = "error"
        self.error = sanitize_error(error, http_status_code=http_status_code)

    def finalize(self) -> dict:
        end_us = _now_us()
        dur_us = max((time.perf_counter_ns() - self._start_perf_ns) // 1_000, 0)
        record = {
            "trace_id": self.pipeline_run_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "category": self.category,
            "start_us": self.start_us,
            "end_us": end_us,
            "dur_us": dur_us,
            "status": self.status,
            "attrs": self.attrs,
            "metrics": self.metrics,
            "error": self.error,
        }
        _append_ndjson("custom-spans.ndjson", record)

        if self.error:
            _append_ndjson(
                "errors.ndjson",
                {
                    "trace_id": self.pipeline_run_id,
                    "span_id": self.span_id,
                    "name": self.name,
                    "category": self.category,
                    "status": self.status,
                    "recorded_at_us": end_us,
                    "error": self.error,
                },
            )

        return record


@contextmanager
def span(
    name: str,
    category: str,
    pipeline_run_id: str,
    parent_span_id: str | None = None,
    **attrs: Any,
) -> Iterator[SpanRecord]:
    record = SpanRecord(
        name=name,
        category=category,
        pipeline_run_id=pipeline_run_id,
        parent_span_id=parent_span_id,
        attrs={"pipeline_run_id": pipeline_run_id, **attrs},
    )
    try:
        yield record
    except Exception as exc:
        if not record.error:
            record.set_error(exc)
        raise
    finally:
        record.finalize()


def write_run_summary(payload: dict) -> None:
    summary = {
        "recorded_at_us": _now_us(),
        **payload,
    }
    _append_ndjson("run-summaries.ndjson", summary)


def load_output_token_baseline() -> dict | None:
    path = _file_path("output-token-baseline.json")
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def compute_output_token_zscore(output_tokens: int) -> float | None:
    baseline = load_output_token_baseline()
    if not baseline:
        return None

    mean = baseline.get("mean")
    stdev = baseline.get("stdev")
    if mean is None or stdev in (None, 0):
        return None

    try:
        zscore = (float(output_tokens) - float(mean)) / float(stdev)
    except (TypeError, ValueError, ZeroDivisionError):
        return None

    return round(zscore, 4)


def export_chrome_trace(source_path: str | Path | None = None, destination_path: str | Path | None = None) -> Path:
    source = Path(source_path) if source_path else _file_path("custom-spans.ndjson")
    destination = Path(destination_path) if destination_path else _file_path("chrome-trace.json")
    events = []

    if source.exists():
        for line in source.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            event = {
                "name": record["name"],
                "cat": record["category"],
                "ph": "X",
                "ts": record["start_us"],
                "dur": record["dur_us"],
                "pid": 1,
                "tid": record.get("attrs", {}).get("route", "recruiter-tool"),
                "args": {
                    "pipeline_run_id": record["trace_id"],
                    **record.get("attrs", {}),
                    **record.get("metrics", {}),
                },
            }
            if record.get("error"):
                event["args"]["error"] = record["error"]
            events.append(event)

    destination.write_text(json.dumps(events, ensure_ascii=True, separators=(",", ":")), encoding="utf-8")
    return destination
