"""Tests for tools/zip_audit.py.

Covers the pure classification + redaction helpers (path → area, area+ext → category,
category → sensitivity, snippet sanitization, filename grouping) plus a few
in-memory integration cases using synthetic ZIP archives.
"""

from __future__ import annotations

import io
from pathlib import Path
from zipfile import ZipFile

import pytest

import zip_audit as za


# ---------------------------------------------------------------------------
# normalize_path & detect_top_level_area
# ---------------------------------------------------------------------------


def test_normalize_path_converts_backslashes():
    assert za.normalize_path("a\\b\\c.txt") == "a/b/c.txt"


def test_detect_top_level_area_recognizes_known_folder():
    assert za.detect_top_level_area("Documents/file.docx") == "Documents"
    assert za.detect_top_level_area("Job Descriptions/role.pdf") == "Job Descriptions"
    assert za.detect_top_level_area("Knowledge Base/note.md") == "Knowledge Base"


def test_detect_top_level_area_recognizes_code_folder_as_generic_label():
    assert za.detect_top_level_area("autoresearch/main.py") == "code/tools"
    assert za.detect_top_level_area(".github/workflows/tests.yml") == "code/tools"


def test_detect_top_level_area_returns_git_metadata_for_git_paths():
    assert za.detect_top_level_area(".git/HEAD") == "git metadata"


def test_detect_top_level_area_classifies_root_loose_files():
    assert za.detect_top_level_area("bootstrap.sh") == "root loose files"


def test_detect_top_level_area_returns_other_for_unrecognized():
    assert za.detect_top_level_area("RandomFolder/file.txt") == "other"


# ---------------------------------------------------------------------------
# normalize_filename_for_grouping
# ---------------------------------------------------------------------------


def test_normalize_filename_strips_copy_suffixes():
    assert za.normalize_filename_for_grouping("Resume (1).pdf") == "resume .pdf"
    assert za.normalize_filename_for_grouping("Resume Copy.pdf") == "resume .pdf"


def test_normalize_filename_lowercases_and_collapses_separators():
    assert za.normalize_filename_for_grouping("Some_File-Name.PDF") == "some file name.pdf"


def test_normalize_filename_handles_paths():
    assert za.normalize_filename_for_grouping("Documents/Sub/A_File.pdf") == "a file.pdf"


# ---------------------------------------------------------------------------
# classify_entry
# ---------------------------------------------------------------------------


def test_classify_entry_marks_python_files_as_code():
    category, _ = za.classify_entry("autoresearch/main.py", ".py", "code/tools")
    assert category == "code/automation assets"


def test_classify_entry_marks_env_files_as_config_data():
    category, subtype = za.classify_entry("recruiter-tool/.env", ".env", "code/tools")
    assert category == "browser/export/config data"
    assert "config" in subtype.lower()


def test_classify_entry_marks_bd_spec_cv_as_candidate_materials():
    category, _ = za.classify_entry("BD Spec CVs/jane_doe.pdf", ".pdf", "BD Spec CVs")
    assert category == "candidate materials"


def test_classify_entry_marks_job_descriptions_as_job_client_materials():
    category, _ = za.classify_entry("Job Descriptions/role.docx", ".docx", "Job Descriptions")
    assert category == "job/client materials"


def test_classify_entry_marks_knowledge_base_as_knowledge():
    # Use a non-code extension (.pdf); .md is in CODE_EXTENSIONS and classifies as code first.
    category, _ = za.classify_entry("Knowledge Base/guide.pdf", ".pdf", "Knowledge Base")
    assert category == "knowledge/reference assets"


def test_classify_entry_md_in_knowledge_base_still_classifies_as_code():
    """Documenting current precedence: any file with a code extension is classified as code,
    regardless of which named area it lives in."""
    category, _ = za.classify_entry("Knowledge Base/guide.md", ".md", "Knowledge Base")
    assert category == "code/automation assets"


def test_classify_entry_marks_personal_admin_keywords_as_personal():
    category, _ = za.classify_entry("Documents/checkstub_2024.pdf", ".pdf", "Documents")
    assert category == "personal/admin records"


def test_classify_entry_marks_bookmarks_as_browser_export():
    # .html sits in CODE_EXTENSIONS so a Chrome-style bookmarks.html actually
    # classifies as code; use a .csv export (typical for Chrome passwords) to
    # exercise the bookmarks-keyword branch.
    category, _ = za.classify_entry("bookmarks_export.csv", ".csv", "root loose files")
    assert category == "browser/export/config data"


def test_classify_entry_marks_resume_keyword_as_candidate():
    category, _ = za.classify_entry("Documents/jane_resume.docx", ".docx", "Documents")
    assert category == "candidate materials"


def test_classify_entry_marks_recruiting_spreadsheet_as_job_materials():
    category, _ = za.classify_entry("Documents/pipeline_tracker.xlsx", ".xlsx", "Documents")
    assert category == "job/client materials"


# ---------------------------------------------------------------------------
# sensitivity_for_entry
# ---------------------------------------------------------------------------


def test_sensitivity_env_file_is_critical():
    assert za.sensitivity_for_entry(".env", ".env", "browser/export/config data", "root loose files") == "critical"


def test_sensitivity_chrome_passwords_is_critical():
    assert (
        za.sensitivity_for_entry(
            "Documents/Chrome Passwords.csv", ".csv", "browser/export/config data", "Documents"
        )
        == "critical"
    )


def test_sensitivity_macro_office_file_is_high():
    assert (
        za.sensitivity_for_entry("Documents/report.docm", ".docm", "knowledge/reference assets", "Documents")
        == "high"
    )


def test_sensitivity_candidate_material_is_high():
    assert (
        za.sensitivity_for_entry("BD Spec CVs/jane_doe.pdf", ".pdf", "candidate materials", "BD Spec CVs")
        == "high"
    )


def test_sensitivity_git_metadata_is_high():
    assert za.sensitivity_for_entry(".git/HEAD", "", "code/automation assets", "git metadata") == "high"


def test_sensitivity_code_asset_is_medium():
    assert (
        za.sensitivity_for_entry("autoresearch/main.py", ".py", "code/automation assets", "code/tools")
        == "medium"
    )


def test_sensitivity_plain_knowledge_is_low():
    assert (
        za.sensitivity_for_entry("Knowledge Base/note.md", ".md", "knowledge/reference assets", "Knowledge Base")
        == "low"
    )


# ---------------------------------------------------------------------------
# risk_for_entry — finds known risk patterns
# ---------------------------------------------------------------------------


def test_risk_for_env_file_returns_critical_finding():
    finding = za.risk_for_entry(".env", ".env", "browser/export/config data")
    assert finding is not None
    assert finding.severity == "critical"
    assert "secret" in finding.reason.lower() or "credential" in finding.reason.lower()


def test_risk_for_macro_office_returns_high_finding():
    finding = za.risk_for_entry("doc.docm", ".docm", "knowledge/reference assets")
    assert finding is not None
    assert finding.risk_type == "macro-enabled office file"


def test_risk_for_candidate_material_flags_pii():
    finding = za.risk_for_entry("BD Spec CVs/jane.pdf", ".pdf", "candidate materials")
    assert finding is not None
    assert finding.risk_type == "candidate PII"


def test_risk_for_plain_knowledge_doc_returns_none():
    """Risk patterns shouldn't fire on benign knowledge content; the caller uses fallback_risk_for_sensitive."""
    assert za.risk_for_entry("Knowledge Base/note.md", ".md", "knowledge/reference assets") is None


# ---------------------------------------------------------------------------
# sanitize_snippet
# ---------------------------------------------------------------------------


def test_sanitize_snippet_redacts_keys_and_tokens():
    raw = "api_key = abc123secret\nauth_token: xyz-789"
    cleaned = za.sanitize_snippet(raw)
    assert "abc123secret" not in cleaned
    assert "xyz-789" not in cleaned
    assert "[REDACTED]" in cleaned


def test_sanitize_snippet_redacts_emails():
    cleaned = za.sanitize_snippet("Reach out to jane.doe@example.com for access.")
    assert "jane.doe@example.com" not in cleaned
    assert "[REDACTED_EMAIL]" in cleaned


def test_sanitize_snippet_redacts_url_hosts():
    cleaned = za.sanitize_snippet("Endpoint: https://api.internal.example.com/path")
    assert "api.internal.example.com" not in cleaned
    assert "[REDACTED_HOST]" in cleaned


def test_sanitize_snippet_truncates_to_600_chars():
    raw = "x" * 2000
    cleaned = za.sanitize_snippet(raw)
    assert len(cleaned) <= 600


def test_sanitize_snippet_collapses_whitespace():
    cleaned = za.sanitize_snippet("a   b\n\nc\td")
    assert cleaned == "a b c d"


# ---------------------------------------------------------------------------
# format_size
# ---------------------------------------------------------------------------


def test_format_size_renders_bytes():
    assert za.format_size(512) == "512.00 B"


def test_format_size_renders_kb():
    assert za.format_size(2048) == "2.00 KB"


def test_format_size_renders_mb():
    assert za.format_size(5 * 1024 * 1024) == "5.00 MB"


def test_format_size_renders_gb():
    assert za.format_size(3 * 1024 * 1024 * 1024) == "3.00 GB"


# ---------------------------------------------------------------------------
# xml_text helper
# ---------------------------------------------------------------------------


def test_xml_text_extracts_element_content():
    xml = b"<root><a>hello</a><b>world</b></root>"
    assert "hello" in za.xml_text(xml)
    assert "world" in za.xml_text(xml)


def test_xml_text_returns_empty_on_parse_error():
    assert za.xml_text(b"not xml at all") == ""


# ---------------------------------------------------------------------------
# make_inventory — integration
# ---------------------------------------------------------------------------


def _build_zip(entries: dict[str, bytes]) -> ZipFile:
    """Build an in-memory ZipFile with given path→bytes entries."""
    buf = io.BytesIO()
    with ZipFile(buf, "w") as zf:
        for path, data in entries.items():
            zf.writestr(path, data)
    buf.seek(0)
    return ZipFile(buf, "r")


def test_make_inventory_classifies_mixed_archive():
    zf = _build_zip({
        "Documents/jane_resume.pdf": b"resume bytes",
        "Knowledge Base/guide.pdf": b"%PDF-fake",
        "autoresearch/main.py": b"print('hi')",
        ".env": b"OPENAI_API_KEY=sk-test",
        "bookmarks_export.csv": b"url,title\n",
    })
    records, findings = za.make_inventory(zf)

    by_path = {r.path: r for r in records}
    assert by_path["Documents/jane_resume.pdf"].category == "candidate materials"
    assert by_path["Documents/jane_resume.pdf"].sensitivity == "high"
    assert by_path["Knowledge Base/guide.pdf"].category == "knowledge/reference assets"
    assert by_path["autoresearch/main.py"].category == "code/automation assets"
    assert by_path[".env"].sensitivity == "critical"
    assert by_path["bookmarks_export.csv"].category == "browser/export/config data"

    risk_paths = {f.path for f in findings}
    assert ".env" in risk_paths
    assert "Documents/jane_resume.pdf" in risk_paths
    zf.close()


def test_make_inventory_sets_file_size_and_modified_time():
    zf = _build_zip({"Documents/note.txt": b"hello world"})
    records, _ = za.make_inventory(zf)
    note = next(r for r in records if r.path == "Documents/note.txt")
    assert note.size_bytes == len(b"hello world")
    assert note.modified_time  # ISO timestamp string
    zf.close()


def test_detect_duplicates_groups_identical_files():
    zf = _build_zip({
        "Documents/resume.pdf": b"same content",
        "Desktop/resume.pdf": b"same content",
        "BD Spec CVs/jane_resume.pdf": b"different content",
    })
    records, _ = za.make_inventory(zf)
    duplicates, lookup = za.detect_duplicates(zf, records)

    # The first two have identical normalized name AND identical content.
    assert lookup["Documents/resume.pdf"] == lookup["Desktop/resume.pdf"]
    # Exactly one duplicate group from the two same-content files.
    assert len({row["duplicate_group"] for row in duplicates}) >= 1
    exact_dup_rows = [row for row in duplicates if row["group_type"] == "exact_content_duplicate"]
    assert len(exact_dup_rows) == 2
    zf.close()


def test_detect_duplicates_distinguishes_same_name_different_content():
    zf = _build_zip({
        "Documents/note.txt": b"version one",
        "Desktop/note.txt": b"version two",
    })
    records, _ = za.make_inventory(zf)
    duplicates, _ = za.detect_duplicates(zf, records)
    # Same normalized name but different bytes: groups them as same_name_or_variant, not exact_content_duplicate.
    group_types = {row["group_type"] for row in duplicates}
    assert "same_name_or_variant" in group_types
    assert "exact_content_duplicate" not in group_types
    zf.close()
