"""Tests for Flask routes in app.py.

Covers route paths that the existing test_telemetry_v1.py did not exercise:
candidate detail, export, attachment upload/list/download/delete, plus error
branches (missing transcript, malformed JSON, candidate-not-found, etc.).
"""

from __future__ import annotations

import io
import os

import pytest

from _fakes import FakeClient, FakeResponse, VALID_CANDIDATE_PAYLOAD


def _install_fake_extraction(app_stack, payload=None):
    payload = payload or dict(VALID_CANDIDATE_PAYLOAD)
    app_stack.ai_processor.get_client = lambda: FakeClient([FakeResponse(payload)])


# ---------------------------------------------------------------------------
# /api/process — additional cases not in test_telemetry_v1.py
# ---------------------------------------------------------------------------


def test_process_rejects_missing_transcript_with_400(app_stack, client):
    _install_fake_extraction(app_stack)
    response = client.post("/api/process", json={"transcript": "", "search_tags": []})
    assert response.status_code == 400
    assert "No transcript" in response.get_json()["error"]


def test_process_rejects_empty_json_with_400(app_stack, client):
    response = client.post("/api/process", json={})
    assert response.status_code == 400


def test_process_ignores_non_list_search_tags(app_stack, client):
    """If search_tags is not a list, it should be coerced to [] not blow up."""
    _install_fake_extraction(app_stack)
    response = client.post(
        "/api/process",
        json={"transcript": "Jane Doe works at Acme Bio.", "search_tags": "not-a-list"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["search_tags"] == []


def test_process_returns_candidate_id_and_brief(app_stack, client):
    _install_fake_extraction(app_stack)
    response = client.post(
        "/api/process",
        json={"transcript": "Jane Doe works at Acme Bio.", "search_tags": ["Aditum"]},
    )
    body = response.get_json()
    assert body["success"] is True
    assert isinstance(body["candidate_id"], int)
    assert "Jane Doe" in body["brief"]


# ---------------------------------------------------------------------------
# /api/search
# ---------------------------------------------------------------------------


def test_search_returns_empty_list_when_no_candidates(app_stack, client):
    response = client.get("/api/search")
    assert response.status_code == 200
    body = response.get_json()
    assert body["count"] == 0
    assert body["candidates"] == []


def test_search_returns_inserted_candidate(app_stack, client):
    _install_fake_extraction(app_stack)
    client.post(
        "/api/process",
        json={"transcript": "Jane Doe works at Acme Bio.", "search_tags": []},
    )

    response = client.get("/api/search?company=Acme")
    body = response.get_json()
    assert body["count"] == 1
    assert body["candidates"][0]["current_company"] == "Acme Bio"


def test_search_drops_blank_filter_values(app_stack, client):
    """Empty query-string values must not turn into LIKE '%%' matches that exclude rows."""
    _install_fake_extraction(app_stack)
    client.post(
        "/api/process",
        json={"transcript": "Jane Doe works at Acme Bio.", "search_tags": []},
    )
    response = client.get("/api/search?company=&therapeutic_area=")
    assert response.status_code == 200
    assert response.get_json()["count"] == 1


# ---------------------------------------------------------------------------
# /api/candidate/<id>
# ---------------------------------------------------------------------------


def test_get_candidate_returns_404_when_missing(app_stack, client):
    response = client.get("/api/candidate/9999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Candidate not found"


def test_get_candidate_returns_candidate_and_brief(app_stack, client):
    _install_fake_extraction(app_stack)
    create = client.post(
        "/api/process",
        json={"transcript": "Jane Doe works at Acme Bio.", "search_tags": []},
    )
    candidate_id = create.get_json()["candidate_id"]

    response = client.get(f"/api/candidate/{candidate_id}")
    assert response.status_code == 200
    body = response.get_json()
    assert body["candidate"]["name"] == "Jane Doe"
    assert "Jane Doe" in body["brief"]


# ---------------------------------------------------------------------------
# /api/export
# ---------------------------------------------------------------------------


def test_export_returns_empty_string_when_no_candidates(app_stack, client):
    response = client.post("/api/export", json={"filters": {}})
    assert response.status_code == 200
    body = response.get_json()
    assert body["count"] == 0
    assert body["export_text"] == ""


def test_export_concatenates_candidate_briefs(app_stack, client):
    _install_fake_extraction(app_stack)
    for transcript in ("Jane Doe works at Acme Bio.", "Jane Doe at Acme Bio leads programs."):
        app_stack.ai_processor.get_client = lambda: FakeClient([FakeResponse(dict(VALID_CANDIDATE_PAYLOAD))])
        client.post("/api/process", json={"transcript": transcript, "search_tags": []})

    response = client.post("/api/export", json={"filters": {}})
    body = response.get_json()
    assert body["count"] == 2
    # Both briefs concatenated; the separator banner should appear twice.
    assert body["export_text"].count("CANDIDATE #") == 2
    assert body["export_text"].count("CANDIDATE #1") == 1
    assert body["export_text"].count("CANDIDATE #2") == 1


def test_export_honors_filters(app_stack, client):
    _install_fake_extraction(app_stack)
    client.post("/api/process", json={"transcript": "Jane Doe at Acme Bio.", "search_tags": []})
    app_stack.ai_processor.get_client = lambda: FakeClient([FakeResponse(
        dict(VALID_CANDIDATE_PAYLOAD, name="Otto", current_company="Beta")
    )])
    client.post("/api/process", json={"transcript": "Otto at Beta.", "search_tags": []})

    response = client.post("/api/export", json={"filters": {"company": "Acme"}})
    body = response.get_json()
    assert body["count"] == 1
    assert "Jane Doe" in body["export_text"]
    assert "Otto" not in body["export_text"]


def test_export_accepts_empty_json_body(app_stack, client):
    response = client.post("/api/export", json={})
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# /api/candidate/<id>/upload
# ---------------------------------------------------------------------------


def test_upload_rejects_request_with_no_file(app_stack, client):
    response = client.post("/api/candidate/1/upload", data={"description": "no file here"})
    assert response.status_code == 400
    assert "No file provided" in response.get_json()["error"]


def test_upload_rejects_disallowed_extension(app_stack, client):
    payload = {
        "file": (io.BytesIO(b"binary"), "evil.exe"),
        "description": "bad",
    }
    response = client.post(
        "/api/candidate/1/upload", data=payload, content_type="multipart/form-data"
    )
    # ValueError raised by file_handler is mapped to 400 by the upload route's except branch.
    assert response.status_code == 400
    assert "File type not allowed" in response.get_json()["error"]


def test_upload_persists_file_and_returns_attachment_id(app_stack, client):
    payload = {
        "file": (io.BytesIO(b"resume bytes"), "resume.pdf"),
        "description": "submitted CV",
    }
    response = client.post(
        "/api/candidate/1/upload", data=payload, content_type="multipart/form-data"
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert isinstance(body["attachment_id"], int)


# ---------------------------------------------------------------------------
# /api/candidate/<id>/attachments
# ---------------------------------------------------------------------------


def test_get_attachments_returns_empty_list_for_candidate_with_none(app_stack, client):
    response = client.get("/api/candidate/1/attachments")
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["attachments"] == []


def test_get_attachments_returns_uploaded_files(app_stack, client):
    upload = {
        "file": (io.BytesIO(b"data"), "doc.pdf"),
        "description": "first",
    }
    client.post("/api/candidate/5/upload", data=upload, content_type="multipart/form-data")

    response = client.get("/api/candidate/5/attachments")
    body = response.get_json()
    assert len(body["attachments"]) == 1
    assert body["attachments"][0]["file_name"] == "doc.pdf"


# ---------------------------------------------------------------------------
# /api/attachment/<id>/download
# ---------------------------------------------------------------------------


def test_download_returns_404_for_unknown_attachment(app_stack, client):
    response = client.get("/api/attachment/9999/download")
    assert response.status_code == 404


def test_download_returns_file_contents(app_stack, client):
    upload = {
        "file": (io.BytesIO(b"the file body"), "report.txt"),
        "description": "download test",
    }
    upload_response = client.post(
        "/api/candidate/3/upload", data=upload, content_type="multipart/form-data"
    )
    attachment_id = upload_response.get_json()["attachment_id"]

    response = client.get(f"/api/attachment/{attachment_id}/download")
    assert response.status_code == 200
    assert response.data == b"the file body"


def test_download_returns_404_when_file_missing_from_disk(app_stack, client):
    upload = {"file": (io.BytesIO(b"x"), "x.txt"), "description": ""}
    upload_response = client.post(
        "/api/candidate/9/upload", data=upload, content_type="multipart/form-data"
    )
    attachment_id = upload_response.get_json()["attachment_id"]

    # Delete the file behind the database's back.
    candidate_dir = os.path.join(app_stack.file_handler.UPLOAD_FOLDER, "9")
    for name in os.listdir(candidate_dir):
        os.remove(os.path.join(candidate_dir, name))

    response = client.get(f"/api/attachment/{attachment_id}/download")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# /api/attachment/<id> DELETE
# ---------------------------------------------------------------------------


def test_delete_attachment_removes_record(app_stack, client):
    upload = {"file": (io.BytesIO(b"x"), "x.txt"), "description": ""}
    upload_response = client.post(
        "/api/candidate/4/upload", data=upload, content_type="multipart/form-data"
    )
    attachment_id = upload_response.get_json()["attachment_id"]

    delete_response = client.delete(f"/api/attachment/{attachment_id}")
    assert delete_response.status_code == 200
    assert delete_response.get_json()["success"] is True

    # Subsequent download should now 404.
    assert client.get(f"/api/attachment/{attachment_id}/download").status_code == 404


def test_delete_attachment_with_unknown_id_returns_200(app_stack, client):
    """delete_attachment is a no-op on unknown IDs, so the route returns success."""
    response = client.delete("/api/attachment/99999")
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Cross-cutting: every route emits the X-Pipeline-Run-Id header
# ---------------------------------------------------------------------------


def test_every_instrumented_route_emits_pipeline_header(app_stack, client):
    _install_fake_extraction(app_stack)

    process = client.post("/api/process", json={"transcript": "Jane Doe at Acme Bio.", "search_tags": []})
    candidate_id = process.get_json()["candidate_id"]

    upload = {"file": (io.BytesIO(b"y"), "y.txt"), "description": ""}
    upload_response = client.post(
        f"/api/candidate/{candidate_id}/upload", data=upload, content_type="multipart/form-data"
    )
    attachment_id = upload_response.get_json()["attachment_id"]

    routes = [
        process,
        client.get("/api/search"),
        client.get(f"/api/candidate/{candidate_id}"),
        client.post("/api/export", json={}),
        upload_response,
        client.get(f"/api/candidate/{candidate_id}/attachments"),
        client.get(f"/api/attachment/{attachment_id}/download"),
        client.delete(f"/api/attachment/{attachment_id}"),
    ]
    for response in routes:
        assert "X-Pipeline-Run-Id" in response.headers, response.request.path
