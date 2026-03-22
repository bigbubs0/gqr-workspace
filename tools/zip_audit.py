from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
import xml.etree.ElementTree as ET


KNOWN_TOP_LEVEL = {
    "Documents",
    "Job Descriptions",
    "BD Spec CVs",
    "Knowledge Base",
    "Desktop",
}
CODE_TOP_LEVEL = {
    ".claude",
    ".github",
    "autoresearch",
    "config",
    "devin-dobek-site",
    "mcp-servers",
    "recruiter-tool",
    "skills",
}
CODE_EXTENSIONS = {
    ".css",
    ".dockerfile",
    ".env",
    ".html",
    ".ini",
    ".ipynb",
    ".js",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".sql",
    ".toml",
    ".tsx",
    ".ts",
    ".yaml",
    ".yml",
}
TEXT_EXTENSIONS = CODE_EXTENSIONS | {
    ".csv",
    ".eml",
    ".gitignore",
    ".gitkeep",
    ".log",
    ".txt",
    ".url",
}
OFFICE_WORD_EXTENSIONS = {".docx", ".docm"}
OFFICE_SHEET_EXTENSIONS = {".xlsx", ".xlsm"}
OPEN_DOCUMENT_EXTENSIONS = {".odt"}
MACRO_EXTENSIONS = {".docm", ".xlsm"}

HIGH_RISK_KEYWORDS = (
    "password",
    "secret",
    "token",
    "credential",
    "vault",
    "confidential",
    "resume",
    "cv",
    "checkstub",
    "benefit",
    "paychex",
    "bookmarks",
    "login",
)
PERSONAL_ADMIN_KEYWORDS = (
    "benefit",
    "checkstub",
    "credit check",
    "paychex",
    "w2",
    "tax",
    "login",
)
KNOWLEDGE_KEYWORDS = (
    "guide",
    "playbook",
    "template",
    "training",
    "newsletter",
    "prompt",
    "review",
    "article",
    "manual",
    "checklist",
    "cookbook",
)
JOB_KEYWORDS = (
    "job description",
    "job desc",
    "jd",
    "open role",
    "opening",
    "search",
    "outsourcing",
    "director",
    "vice president",
    "medical writing",
)


@dataclass
class EntryRecord:
    path: str
    top_level_area: str
    extension: str
    size_bytes: int
    modified_time: str
    is_dir: bool
    category: str
    subtype: str
    sensitivity: str
    review_status: str
    duplicate_group: str


@dataclass
class ReviewRecord:
    path: str
    review_kind: str
    note: str
    snippet: str


@dataclass
class RiskFinding:
    path: str
    risk_type: str
    severity: str
    reason: str
    recommended_action: str


def normalize_path(name: str) -> str:
    return name.replace("\\", "/")


def detect_top_level_area(path: str) -> str:
    if path.startswith(".git/"):
        return "git metadata"
    first = path.split("/", 1)[0]
    if first in KNOWN_TOP_LEVEL:
        return first
    if first in CODE_TOP_LEVEL:
        return "code/tools"
    if "/" not in path:
        return "root loose files"
    return "other"


def normalize_filename_for_grouping(path: str) -> str:
    name = PurePosixPath(path).name.lower()
    name = re.sub(r"\(\d+\)", "", name)
    name = re.sub(r"\bcopy\b", "", name)
    name = re.sub(r"[_\-\s]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def classify_entry(path: str, extension: str, area: str) -> tuple[str, str]:
    lower = path.lower()
    filename = PurePosixPath(path).name.lower()

    if area == "git metadata":
        return "code/automation assets", "git repository snapshot"
    if area == "code/tools" or extension in CODE_EXTENSIONS or filename in {
        "dockerfile",
        "package.json",
        "package-lock.json",
        "requirements.txt",
        "readme.md",
    }:
        if "config" in lower or filename.endswith(".env"):
            return "browser/export/config data", "tool configuration"
        return "code/automation assets", "application or automation code"
    if any(keyword in lower for keyword in PERSONAL_ADMIN_KEYWORDS):
        return "personal/admin records", "financial or employment record"
    if "bookmarks" in lower or "chrome passwords" in lower:
        return "browser/export/config data", "browser export"
    if "vault" in lower or lower.endswith("settings.local.json"):
        return "browser/export/config data", "assistant profile or local settings"
    if area == "BD Spec CVs":
        return "candidate materials", "candidate profile or campaign asset"
    if area == "Job Descriptions":
        return "job/client materials", "job description or role brief"
    if area == "Knowledge Base" or any(keyword in lower for keyword in KNOWLEDGE_KEYWORDS):
        if extension in {".pptx", ".ppt"}:
            return "knowledge/reference assets", "training deck or presentation"
        return "knowledge/reference assets", "playbook, template, or research note"
    if any(token in lower for token in ("resume", " cv", "cv ", "candidate", "interview prep")):
        return "candidate materials", "candidate profile, resume, or prep doc"
    if any(token in lower for token in JOB_KEYWORDS):
        return "job/client materials", "job description, search brief, or outreach asset"
    if extension in {".png", ".jpg", ".jpeg"}:
        return "knowledge/reference assets", "image or screenshot"
    if extension in {".xlsx", ".xls", ".xlsm", ".accdb"}:
        if any(token in lower for token in ("pipeline", "metrics", "candidate", "client", "role")):
            return "job/client materials", "spreadsheet or recruiting tracker"
        return "knowledge/reference assets", "spreadsheet or database"
    return "knowledge/reference assets", "general document archive"


def sensitivity_for_entry(path: str, extension: str, category: str, area: str) -> str:
    lower = path.lower()
    if lower.endswith(".env") or "chrome passwords" in lower:
        return "critical"
    if any(keyword in lower for keyword in ("password", "secret", "token", "credential")):
        return "critical"
    if lower.endswith("settings.local.json"):
        return "critical"
    if "vault" in lower or "bookmarks" in lower:
        return "high"
    if path.startswith(".git/"):
        return "high"
    if extension in MACRO_EXTENSIONS or extension == ".accdb":
        return "high"
    if category in {"candidate materials", "personal/admin records"}:
        return "high"
    if area in {"Documents", "Desktop"} and any(keyword in lower for keyword in HIGH_RISK_KEYWORDS):
        return "high"
    if category in {"browser/export/config data", "code/automation assets"}:
        return "medium"
    return "low"


def risk_for_entry(path: str, extension: str, category: str) -> RiskFinding | None:
    lower = path.lower()
    if lower.endswith(".env"):
        return RiskFinding(
            path=path,
            risk_type="environment secrets",
            severity="critical",
            reason="Environment files often contain API keys, tokens, or service credentials.",
            recommended_action="Move to a secrets-only vault location and exclude from broad backups.",
        )
    if "chrome passwords" in lower:
        return RiskFinding(
            path=path,
            risk_type="password export",
            severity="critical",
            reason="Browser password export files may contain plaintext credentials for multiple services.",
            recommended_action="Delete after secure import or move to encrypted storage immediately.",
        )
    if lower.endswith("settings.local.json") or "token" in lower or "secret" in lower:
        return RiskFinding(
            path=path,
            risk_type="local tool configuration",
            severity="critical",
            reason="Local settings and config files may embed API endpoints, keys, or machine-specific secrets.",
            recommended_action="Review and separate reusable config from machine-local secrets.",
        )
    if path.startswith(".git/"):
        return RiskFinding(
            path=path,
            risk_type="repository metadata",
            severity="high",
            reason="Git history and remote metadata can expose private project structure and recoverable deleted content.",
            recommended_action="Keep repository data isolated with active code projects rather than mixed into document backups.",
        )
    if extension in MACRO_EXTENSIONS:
        return RiskFinding(
            path=path,
            risk_type="macro-enabled office file",
            severity="high",
            reason="Macro-enabled Office documents may contain executable VBA payloads and should not be opened casually.",
            recommended_action="Quarantine and scan before use; preserve only if still operationally needed.",
        )
    if extension == ".accdb":
        return RiskFinding(
            path=path,
            risk_type="local database file",
            severity="high",
            reason="Access databases can contain structured business or personal data that is hard to review at a glance.",
            recommended_action="Move to a controlled data area and document its contents before long-term retention.",
        )
    if category == "candidate materials":
        return RiskFinding(
            path=path,
            risk_type="candidate PII",
            severity="high",
            reason="Candidate resumes, profiles, and submissions contain personal information and career history.",
            recommended_action="Consolidate into a restricted candidate materials archive with retention rules.",
        )
    if category == "personal/admin records":
        return RiskFinding(
            path=path,
            risk_type="personal or payroll data",
            severity="high",
            reason="Administrative records may include payroll, benefits, or personal financial information.",
            recommended_action="Move to an encrypted personal records folder outside the recruiting workspace.",
        )
    if category == "browser/export/config data":
        return RiskFinding(
            path=path,
            risk_type="exported config or browsing data",
            severity="high",
            reason="Exports and tool configuration files can reveal accounts, workflow topology, or internal systems.",
            recommended_action="Split operational config from general backup content and restrict access.",
        )
    return None


def fallback_risk_for_sensitive(path: str, category: str, sensitivity: str) -> RiskFinding:
    risk_type = "sensitive document"
    reason = "This file sits in a high-sensitivity class and should be separated from broad workspace backups."
    action = "Move into a restricted archive with clear retention and access controls."
    if category == "knowledge/reference assets":
        risk_type = "sensitive reference material"
        reason = "This document appears mixed into a workspace backup where confidential or proprietary reference content is broadly accessible."
        action = "Review for business value, then relocate to a curated knowledge archive."
    elif category == "code/automation assets":
        risk_type = "project asset exposure"
        reason = "This file is part of an active code or automation asset that should not be mixed into a general document backup."
        action = "Separate active project assets from document archives and preserve them with project context."
    return RiskFinding(
        path=path,
        risk_type=risk_type,
        severity=sensitivity,
        reason=reason,
        recommended_action=action,
    )


def sanitize_snippet(text: str) -> str:
    cleaned = text.replace("\r", "")
    cleaned = re.sub(
        r"([A-Za-z0-9_]*(?:key|token|secret|password)[A-Za-z0-9_]*\s*[:=]\s*)([^\n]+)",
        r"\1[REDACTED]",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"(https?://)([^/\s:]+)([^\s]*)", r"\1[REDACTED_HOST]\3", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[REDACTED_EMAIL]", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:600]


def xml_text(xml_bytes: bytes) -> str:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return ""
    chunks: list[str] = []
    for element in root.iter():
        if element.text and element.text.strip():
            chunks.append(element.text.strip())
    return " ".join(chunks)


def read_nested_zip_text(blob: bytes, inner_path: str) -> str:
    try:
        with ZipFile(BytesIO(blob)) as nested:
            with nested.open(inner_path) as handle:
                return xml_text(handle.read())
    except Exception:
        return ""


def inspect_office_container(blob: bytes, extension: str) -> tuple[str, str]:
    try:
        with ZipFile(BytesIO(blob)) as nested:
            members = set(nested.namelist())
            if extension in OFFICE_WORD_EXTENSIONS:
                document_text = ""
                if "word/document.xml" in members:
                    with nested.open("word/document.xml") as handle:
                        document_text = xml_text(handle.read())
                macro_flag = "macro-enabled" if "word/vbaProject.bin" in members else "macro-free"
                return document_text, macro_flag
            if extension in OFFICE_SHEET_EXTENSIONS:
                sheet_names = []
                if "xl/workbook.xml" in members:
                    with nested.open("xl/workbook.xml") as handle:
                        xml_blob = handle.read()
                        try:
                            root = ET.fromstring(xml_blob)
                            for sheet in root.iter():
                                if sheet.tag.endswith("sheet"):
                                    name = sheet.attrib.get("name")
                                    if name:
                                        sheet_names.append(name)
                        except ET.ParseError:
                            pass
                macro_flag = "macro-enabled" if "xl/vbaProject.bin" in members else "macro-free"
                summary = f"Workbook sheets: {', '.join(sheet_names[:12])}" if sheet_names else "Workbook structure detected"
                return summary, macro_flag
    except Exception:
        return "", "unreadable"
    return "", "unreadable"


def extract_text_from_entry(zf: ZipFile, path: str, extension: str) -> tuple[str, str]:
    try:
        blob = zf.read(path)
    except Exception:
        return "", "unreadable"
    if extension in TEXT_EXTENSIONS or PurePosixPath(path).name.lower() in {"dockerfile", "head", "main", "config", "description", "packed-refs"}:
        for encoding in ("utf-8", "utf-16", "latin-1"):
            try:
                return blob.decode(encoding), "text"
            except UnicodeDecodeError:
                continue
        return "", "binary-text-like"
    if extension in OFFICE_WORD_EXTENSIONS:
        return inspect_office_container(blob, extension)
    if extension in OFFICE_SHEET_EXTENSIONS:
        return inspect_office_container(blob, extension)
    if extension in OPEN_DOCUMENT_EXTENSIONS:
        return read_nested_zip_text(blob, "content.xml"), "odf"
    if extension == ".pdf":
        try:
            from pypdf import PdfReader  # type: ignore

            reader = PdfReader(BytesIO(blob))
            pages = []
            for page in reader.pages[:2]:
                extracted = page.extract_text() or ""
                if extracted.strip():
                    pages.append(extracted.strip())
            return "\n".join(pages), "pdf"
        except Exception:
            return "", "pdf-unparsed"
    if extension in {".doc", ".ppt", ".xls"}:
        return "", "legacy-office-binary"
    return "", "binary"


def select_sample_paths(records: list[EntryRecord]) -> set[str]:
    chosen: set[str] = set()
    area_limits = {
        "BD Spec CVs": 4,
        "Job Descriptions": 4,
        "Knowledge Base": 4,
        "Documents": 4,
        "Desktop": 4,
        "code/tools": 4,
    }
    priority_patterns = (
        "readme",
        "guide",
        "template",
        "training",
        "review",
        "candidate",
        "job",
        "director",
        "role",
        "pipeline",
        "dashboard",
    )
    by_area: dict[str, list[EntryRecord]] = defaultdict(list)
    for record in records:
        if record.is_dir or record.sensitivity in {"high", "critical"}:
            continue
        if record.top_level_area in area_limits:
            by_area[record.top_level_area].append(record)
    for area, limit in area_limits.items():
        candidates = sorted(
            by_area.get(area, []),
            key=lambda item: (
                not any(pattern in item.path.lower() for pattern in priority_patterns),
                item.extension not in {".md", ".docx", ".odt", ".txt", ".py", ".json"},
                len(item.path),
            ),
        )
        for item in candidates[:limit]:
            chosen.add(item.path)
    return chosen


def compute_hashes(zf: ZipFile, paths: list[str]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in paths:
        digest = hashlib.sha256()
        with zf.open(path) as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
        hashes[path] = digest.hexdigest()
    return hashes


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def make_inventory(zf: ZipFile) -> tuple[list[EntryRecord], list[RiskFinding]]:
    records: list[EntryRecord] = []
    findings: list[RiskFinding] = []
    for info in sorted(zf.infolist(), key=lambda item: normalize_path(item.filename).lower()):
        path = normalize_path(info.filename)
        is_dir = info.is_dir()
        extension = PurePosixPath(path).suffix.lower()
        area = detect_top_level_area(path)
        category, subtype = classify_entry(path, extension, area)
        sensitivity = sensitivity_for_entry(path, extension, category, area)
        record = EntryRecord(
            path=path,
            top_level_area=area,
            extension=extension,
            size_bytes=info.file_size,
            modified_time=datetime(*info.date_time).isoformat(timespec="seconds"),
            is_dir=is_dir,
            category=category,
            subtype=subtype,
            sensitivity=sensitivity,
            review_status="metadata-only",
            duplicate_group="",
        )
        records.append(record)
        if not is_dir and sensitivity in {"high", "critical"}:
            finding = risk_for_entry(path, extension, category) or fallback_risk_for_sensitive(path, category, sensitivity)
            findings.append(finding)
    return records, findings


def detect_duplicates(zf: ZipFile, records: list[EntryRecord]) -> tuple[list[dict[str, str]], dict[str, str]]:
    files = [record for record in records if not record.is_dir]
    grouped: dict[str, list[EntryRecord]] = defaultdict(list)
    for record in files:
        grouped[normalize_filename_for_grouping(record.path)].append(record)

    duplicate_rows: list[dict[str, str]] = []
    duplicate_lookup: dict[str, str] = {}
    group_index = 1
    for normalized_name, group in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        if len(group) < 2:
            continue
        hashes = compute_hashes(zf, [record.path for record in group])
        buckets: dict[tuple[int, str], list[EntryRecord]] = defaultdict(list)
        for record in group:
            buckets[(record.size_bytes, hashes[record.path])].append(record)
        exact_duplicate_detected = any(len(bucket) > 1 for bucket in buckets.values())
        group_id = f"DUP-{group_index:03d}"
        group_index += 1
        best_path = sorted(group, key=lambda item: (item.top_level_area not in {"Documents", "Knowledge Base"}, len(item.path)))[0].path
        for record in sorted(group, key=lambda item: item.path.lower()):
            hash_value = hashes[record.path]
            duplicate_lookup[record.path] = group_id
            recommendation = "keep primary"
            if record.path != best_path:
                recommendation = "collapse into primary copy" if exact_duplicate_detected else "review as versioned variant"
            duplicate_rows.append(
                {
                    "duplicate_group": group_id,
                    "normalized_name": normalized_name,
                    "path": record.path,
                    "size_bytes": str(record.size_bytes),
                    "sha256": hash_value,
                    "group_type": "exact_content_duplicate" if len(buckets[(record.size_bytes, hash_value)]) > 1 else "same_name_or_variant",
                    "recommended_action": recommendation,
                }
            )
    return duplicate_rows, duplicate_lookup


def summarize_snippet(path: str, extracted_text: str, extraction_mode: str) -> str:
    lower = path.lower()
    if lower.endswith(".env"):
        keys = []
        for line in extracted_text.splitlines():
            if "=" in line and not line.strip().startswith("#"):
                keys.append(line.split("=", 1)[0].strip())
        if keys:
            return f"Environment file with keys: {', '.join(keys[:8])}"
        return "Environment file present; values redacted."
    if extraction_mode == "text" and lower.endswith(".json"):
        try:
            data = json.loads(extracted_text)
            if isinstance(data, dict):
                return f"JSON config keys: {', '.join(list(data.keys())[:10])}"
        except Exception:
            pass
    cleaned = sanitize_snippet(extracted_text)
    if cleaned:
        return cleaned
    if extraction_mode in {"macro-free", "macro-enabled"}:
        return f"Office container inspected; status: {extraction_mode}."
    return f"Reviewed as {extraction_mode}; no usable text extracted."


def run_reviews(zf: ZipFile, records: list[EntryRecord]) -> list[ReviewRecord]:
    reviews: list[ReviewRecord] = []
    sample_paths = select_sample_paths(records)
    for record in records:
        if record.is_dir:
            continue
        if record.sensitivity not in {"high", "critical"} and record.path not in sample_paths:
            continue
        extracted_text, extraction_mode = extract_text_from_entry(zf, record.path, record.extension)
        note = summarize_snippet(record.path, extracted_text, extraction_mode)
        review_kind = "high-risk" if record.sensitivity in {"high", "critical"} else "sample"
        record.review_status = f"reviewed-{review_kind}"
        reviews.append(
            ReviewRecord(
                path=record.path,
                review_kind=review_kind,
                note=note,
                snippet=sanitize_snippet(extracted_text) if extracted_text else "",
            )
        )
    return reviews


def make_top_level_summary(records: list[EntryRecord], reviews: list[ReviewRecord], findings: list[RiskFinding]) -> dict[str, object]:
    files = [record for record in records if not record.is_dir]
    directories = [record for record in records if record.is_dir]
    return {
        "archive": {
            "entries": len(records),
            "files": len(files),
            "directories": len(directories),
            "total_uncompressed_bytes": sum(record.size_bytes for record in files),
        },
        "by_top_level_area": {
            area: {
                "files": sum(1 for record in files if record.top_level_area == area),
                "bytes": sum(record.size_bytes for record in files if record.top_level_area == area),
            }
            for area in sorted({record.top_level_area for record in records})
        },
        "by_extension": dict(
            sorted(Counter(record.extension or "[no extension]" for record in files).items(), key=lambda item: (-item[1], item[0]))
        ),
        "by_category": dict(sorted(Counter(record.category for record in files).items(), key=lambda item: (-item[1], item[0]))),
        "by_sensitivity": dict(sorted(Counter(record.sensitivity for record in files).items())),
        "review_status": dict(sorted(Counter(record.review_status for record in files).items())),
        "reviewed_items": len(reviews),
        "high_risk_findings": len(findings),
    }


def format_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024.0 or unit == "GB":
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{num_bytes} B"


def recommendation_taxonomy() -> str:
    return "\n".join(
        [
            "- `Projects/automation`: `autoresearch`, `recruiter-tool`, `.git`, `.github`, `.claude`, `config`, and related code assets",
            "- `Operations/candidate-materials`: resumes, candidate profiles, interview prep docs, and formatted submissions",
            "- `Operations/job-client-materials`: job descriptions, outreach campaigns, open roles, and client intake assets",
            "- `Knowledge/playbooks`: training docs, templates, articles, decks, prompt libraries, and reference notes",
            "- `Personal-admin/restricted`: payroll, benefits, browser exports, login artifacts, local config, password exports, and databases",
            "- `Archive/legacy`: old duplicates, historical copies, and superseded loose root files after review",
        ]
    )


def build_markdown_reports(
    zip_path: Path,
    output_dir: Path,
    reviews: list[ReviewRecord],
    findings: list[RiskFinding],
    duplicates: list[dict[str, str]],
    summary: dict[str, object],
) -> tuple[str, str]:
    by_area = summary["by_top_level_area"]
    by_category = summary["by_category"]
    by_sensitivity = summary["by_sensitivity"]
    duplicate_groups = Counter(row["duplicate_group"] for row in duplicates)
    reviewed_samples: dict[str, list[ReviewRecord]] = defaultdict(list)
    for review in reviews:
        if len(reviewed_samples[review.review_kind]) < 10:
            reviewed_samples[review.review_kind].append(review)

    sprawl_examples = [
        "Candidate and resume materials appear both at the archive root and under `Documents`, `Desktop`, and `BD Spec CVs`.",
        "Reference and training content is split across `Knowledge Base`, `Documents`, root loose files, and `Desktop`.",
        "Operational tooling (`autoresearch`, `recruiter-tool`, `.git`, config files) is mixed into the same backup as confidential recruiting documents.",
    ]
    immediate_priorities = [
        "Move password exports, `.env`, local settings, vault material, browser exports, and database files into a restricted encrypted area.",
        "Consolidate candidate materials from root, `Documents`, `Desktop`, and `BD Spec CVs` into a single controlled archive.",
        "Split active tools and repository metadata into a dedicated project backup separate from recruiting documents.",
        "Deduplicate repeated Green Key files, repeated CV copies, and repeated campaign assets using `duplicates.csv`.",
        "Archive or delete low-value root loose files once their canonical folder destination is established.",
    ]

    audit_lines = [
        "# ZIP Audit Summary",
        "",
        f"Source archive: `{zip_path}`",
        f"Output folder: `{output_dir}`",
        "",
        "## Archive Overview",
        "",
        f"- Entries: {summary['archive']['entries']}",
        f"- Files: {summary['archive']['files']}",
        f"- Directories: {summary['archive']['directories']}",
        f"- Total uncompressed size: {format_size(summary['archive']['total_uncompressed_bytes'])}",
        f"- High-risk findings: {len(findings)}",
        f"- Reviewed files: {len(reviews)}",
        f"- Duplicate groups confirmed: {len(duplicate_groups)}",
        "",
        "This backup is a mixed recruiting workspace archive. It combines candidate and client documents, a knowledge/reference library, personal/admin records, and active automation/code projects with retained Git metadata.",
        "",
        "## Major Content Areas",
        "",
    ]
    for area, info in sorted(by_area.items(), key=lambda item: (-item[1]["files"], item[0])):
        audit_lines.append(f"- `{area}`: {info['files']} files, {format_size(info['bytes'])}")
    audit_lines += ["", "Category mix:", ""]
    for category, count in sorted(by_category.items(), key=lambda item: (-item[1], item[0])):
        audit_lines.append(f"- `{category}`: {count} files")
    audit_lines += ["", "## Organization Problems", ""]
    audit_lines.extend(f"- {line}" for line in sprawl_examples)
    audit_lines += [
        "",
        "Notable duplicate pressure points:",
        "",
        "- Repeated Green Key administrative/reference files appear in multiple folders.",
        "- Resume and candidate-profile copies recur between root files, `Documents`, and `BD Spec CVs`.",
        "- Root loose files include operationally important materials that should sit under a named project or workflow folder.",
        "",
        "## Sensitive / High-Risk Findings",
        "",
    ]
    for severity, count in sorted(by_sensitivity.items()):
        audit_lines.append(f"- `{severity}` sensitivity: {count} files")
    audit_lines += [
        "",
        "Key risk clusters:",
        "",
        "- Credentials/config: `.env`, local assistant settings, operational JSON config, bookmarks exports, and Git metadata.",
        "- Candidate PII: resumes, confidential candidate documents, and formatted submission materials across several folders.",
        "- Personal/admin records: benefits, payroll/checkstub-style files, and personal database files embedded in the same archive.",
        "- Macro or opaque data stores: macro-enabled Office docs and Access databases that deserve quarantine before casual reuse.",
        "",
        "Representative reviewed items:",
        "",
    ]
    for review in reviewed_samples["high-risk"][:8]:
        audit_lines.append(f"- `{review.path}`: {review.note}")
    audit_lines += [
        "",
        "## Code / Tooling Assets",
        "",
        "- `autoresearch`: an eval-driven recruiting-skill optimization package with prompts, tests, results, and shell scripts.",
        "- `recruiter-tool`: a local Python web app for candidate intake processing and SQLite-backed storage.",
        "- `.git` and `.github`: a live repository snapshot, including pack files and remote metadata.",
        "- `Documents/Bryan's Vault`: a structured operating vault with plans, dashboards, memories, and skill/config artifacts.",
        "",
        "Representative code/tool reviews:",
        "",
    ]
    for review in reviewed_samples["sample"][:8]:
        audit_lines.append(f"- `{review.path}`: {review.note}")
    audit_lines += [
        "",
        "## Duplicate and Consolidation Opportunities",
        "",
        f"- Duplicate groups in `duplicates.csv`: {len(duplicate_groups)}",
        f"- Files participating in duplicate groups: {len(duplicates)}",
        "- Highest-yield consolidation targets are repeated resumes, duplicated Green Key documents, and recurring job/campaign artifacts.",
        "- Use exact-content duplicates for safe collapse first, then review same-name variants as possible revisions rather than identical copies.",
        "",
        "## Recommended Folder Taxonomy",
        "",
        recommendation_taxonomy(),
        "",
        "## Immediate Cleanup Priorities",
        "",
    ]
    audit_lines.extend(f"- {line}" for line in immediate_priorities)

    executive_lines = [
        "# Executive Summary",
        "",
        f"`{zip_path.name}` is not a single project backup. It is a mixed recruiting workspace containing candidate files, job/client materials, knowledge assets, personal/admin records, and live automation/code assets.",
        "",
        "The largest organizational issue is sprawl. Candidate and recruiting documents are spread across root files, `Documents`, `Desktop`, `BD Spec CVs`, `Job Descriptions`, and `Knowledge Base`, while active tool projects and repository metadata sit alongside confidential business material.",
        "",
        "The highest-risk items are password exports, `.env` files, local config/settings, Git metadata, payroll/benefits records, databases, and the large body of candidate resumes and confidential submissions. Those should be isolated before any broader cleanup.",
        "",
        "The most valuable active assets appear to be `autoresearch`, `recruiter-tool`, the Git repository snapshot, and the structured `Bryan's Vault` materials. Those should be preserved as project assets rather than treated like document clutter.",
        "",
        "Best next moves: isolate secrets and personal/admin records, consolidate candidate materials into one restricted archive, split code/projects into a dedicated backup area, then use `duplicates.csv` to collapse repeated CV and Green Key copies.",
    ]
    return "\n".join(audit_lines) + "\n", "\n".join(executive_lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit a mixed-workspace ZIP archive without extracting it.")
    parser.add_argument("zip_path", type=Path, help="Path to the ZIP archive to audit")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("zip-audit-output") / "gqr-workspace-backup",
        help="Directory where audit artifacts will be written",
    )
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    with ZipFile(args.zip_path) as zf:
        records, findings = make_inventory(zf)
        duplicates, duplicate_lookup = detect_duplicates(zf, records)
        for record in records:
            if record.path in duplicate_lookup:
                record.duplicate_group = duplicate_lookup[record.path]
        reviews = run_reviews(zf, records)
        summary = make_top_level_summary(records, reviews, findings)
        audit_report, executive_summary = build_markdown_reports(
            args.zip_path.resolve(),
            output_dir,
            reviews,
            findings,
            duplicates,
            summary,
        )

    inventory_rows = [
        {
            "path": record.path,
            "top_level_area": record.top_level_area,
            "extension": record.extension,
            "size_bytes": str(record.size_bytes),
            "modified_time": record.modified_time,
            "is_dir": "1" if record.is_dir else "0",
            "category": record.category,
            "subtype": record.subtype,
            "sensitivity": record.sensitivity,
            "review_status": record.review_status,
            "duplicate_group": record.duplicate_group,
        }
        for record in records
    ]
    risk_rows = [
        {
            "path": finding.path,
            "risk_type": finding.risk_type,
            "severity": finding.severity,
            "reason": finding.reason,
            "recommended_action": finding.recommended_action,
        }
        for finding in findings
    ]

    write_csv(
        output_dir / "inventory.csv",
        inventory_rows,
        [
            "path",
            "top_level_area",
            "extension",
            "size_bytes",
            "modified_time",
            "is_dir",
            "category",
            "subtype",
            "sensitivity",
            "review_status",
            "duplicate_group",
        ],
    )
    write_csv(
        output_dir / "duplicates.csv",
        duplicates,
        [
            "duplicate_group",
            "normalized_name",
            "path",
            "size_bytes",
            "sha256",
            "group_type",
            "recommended_action",
        ],
    )
    write_csv(
        output_dir / "high-risk-findings.csv",
        risk_rows,
        ["path", "risk_type", "severity", "reason", "recommended_action"],
    )
    (output_dir / "top_level_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "audit-summary.md").write_text(audit_report, encoding="utf-8")
    (output_dir / "executive-summary.md").write_text(executive_summary, encoding="utf-8")

    print(json.dumps({"output_dir": str(output_dir), "files_written": 6, "reviewed_files": len(reviews)}, indent=2))


if __name__ == "__main__":
    main()
