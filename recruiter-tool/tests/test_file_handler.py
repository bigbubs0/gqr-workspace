"""Tests for file_handler.py — uploads, attachment lookup, deletion."""

from __future__ import annotations

import io
import os
import sqlite3

import pytest
from werkzeug.datastructures import FileStorage


def _make_upload(filename: str, content: bytes = b"hello") -> FileStorage:
    return FileStorage(stream=io.BytesIO(content), filename=filename)


def test_allowed_file_accepts_known_extensions(app_stack):
    fh = app_stack.file_handler
    assert fh.allowed_file("resume.pdf") is True
    assert fh.allowed_file("brief.docx") is True
    assert fh.allowed_file("interview.mp3") is True
    assert fh.allowed_file("photo.jpg") is True


def test_allowed_file_is_case_insensitive(app_stack):
    fh = app_stack.file_handler
    assert fh.allowed_file("RESUME.PDF") is True
    assert fh.allowed_file("Resume.Docx") is True


def test_allowed_file_rejects_unknown_extensions(app_stack):
    fh = app_stack.file_handler
    assert fh.allowed_file("malware.exe") is False
    assert fh.allowed_file("script.sh") is False
    assert fh.allowed_file("noextension") is False


def test_init_upload_folder_creates_directory(app_stack):
    fh = app_stack.file_handler
    fh.init_upload_folder()
    assert os.path.isdir(fh.UPLOAD_FOLDER)


def test_save_attachment_returns_none_for_missing_file(app_stack):
    fh = app_stack.file_handler
    assert fh.save_attachment(candidate_id=1, file=None) is None


def test_save_attachment_returns_none_for_empty_filename(app_stack):
    fh = app_stack.file_handler
    empty = FileStorage(stream=io.BytesIO(b""), filename="")
    assert fh.save_attachment(candidate_id=1, file=empty) is None


def test_save_attachment_rejects_disallowed_extension(app_stack):
    app_stack.database.init_db()
    fh = app_stack.file_handler
    with pytest.raises(ValueError, match="File type not allowed"):
        fh.save_attachment(candidate_id=1, file=_make_upload("payload.exe"))


def test_save_attachment_persists_file_to_disk(app_stack):
    app_stack.database.init_db()
    fh = app_stack.file_handler
    fh.init_upload_folder()
    upload = _make_upload("resume.pdf", b"pdf content here")
    attachment_id = fh.save_attachment(candidate_id=42, file=upload, description="initial CV")
    assert isinstance(attachment_id, int)

    stored_dir = os.path.join(fh.UPLOAD_FOLDER, "42")
    assert os.path.isdir(stored_dir)
    assert "resume.pdf" in os.listdir(stored_dir)
    with open(os.path.join(stored_dir, "resume.pdf"), "rb") as fp:
        assert fp.read() == b"pdf content here"


def test_save_attachment_writes_database_row(app_stack):
    app_stack.database.init_db()
    fh = app_stack.file_handler
    fh.init_upload_folder()
    fh.save_attachment(candidate_id=42, file=_make_upload("resume.pdf"), description="initial CV")

    conn = sqlite3.connect(app_stack.database.DB_PATH)
    try:
        row = conn.execute(
            "SELECT candidate_id, file_name, file_type, description FROM attachments"
        ).fetchone()
    finally:
        conn.close()
    assert row == (42, "resume.pdf", "pdf", "initial CV")


def test_save_attachment_uses_secure_filename(app_stack):
    """werkzeug.secure_filename should strip path traversal attempts."""
    app_stack.database.init_db()
    fh = app_stack.file_handler
    fh.init_upload_folder()
    attachment_id = fh.save_attachment(
        candidate_id=1, file=_make_upload("../../etc/passwd.pdf", b"x")
    )
    assert attachment_id is not None

    # No file should appear outside the candidate folder.
    candidate_dir = os.path.join(fh.UPLOAD_FOLDER, "1")
    files = os.listdir(candidate_dir)
    assert len(files) == 1
    assert "/" not in files[0] and ".." not in files[0]


def test_get_attachments_returns_rows_for_candidate(app_stack):
    app_stack.database.init_db()
    fh = app_stack.file_handler
    fh.init_upload_folder()
    fh.save_attachment(candidate_id=1, file=_make_upload("a.pdf"), description="first")
    fh.save_attachment(candidate_id=1, file=_make_upload("b.docx"), description="second")
    fh.save_attachment(candidate_id=2, file=_make_upload("c.pdf"), description="other")

    rows = fh.get_attachments(1)
    names = {row["file_name"] for row in rows}
    assert names == {"a.pdf", "b.docx"}


def test_get_attachments_returns_empty_for_unknown_candidate(app_stack):
    app_stack.database.init_db()
    fh = app_stack.file_handler
    assert fh.get_attachments(9999) == []


def test_delete_attachment_removes_db_row_and_file(app_stack):
    app_stack.database.init_db()
    fh = app_stack.file_handler
    fh.init_upload_folder()
    attachment_id = fh.save_attachment(candidate_id=7, file=_make_upload("doomed.pdf"))
    file_path = os.path.join(fh.UPLOAD_FOLDER, "7", "doomed.pdf")
    assert os.path.exists(file_path)

    fh.delete_attachment(attachment_id)

    assert not os.path.exists(file_path)
    conn = sqlite3.connect(app_stack.database.DB_PATH)
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM attachments WHERE id = ?", (attachment_id,)
        ).fetchone()[0]
    finally:
        conn.close()
    assert count == 0


def test_delete_attachment_handles_missing_file_gracefully(app_stack):
    """If the row exists but the file was deleted out-of-band, delete_attachment must not raise."""
    app_stack.database.init_db()
    fh = app_stack.file_handler
    fh.init_upload_folder()
    attachment_id = fh.save_attachment(candidate_id=8, file=_make_upload("vanished.pdf"))
    file_path = os.path.join(fh.UPLOAD_FOLDER, "8", "vanished.pdf")
    os.remove(file_path)  # delete file behind the database's back

    fh.delete_attachment(attachment_id)  # should not raise

    conn = sqlite3.connect(app_stack.database.DB_PATH)
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM attachments WHERE id = ?", (attachment_id,)
        ).fetchone()[0]
    finally:
        conn.close()
    assert count == 0


def test_delete_attachment_with_unknown_id_is_noop(app_stack):
    app_stack.database.init_db()
    fh = app_stack.file_handler
    fh.delete_attachment(99999)  # no exception
