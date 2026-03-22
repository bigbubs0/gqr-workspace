from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import json
import re
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from shutil import which
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
TASK_DIR = SCRIPT_DIR.parent
REFERENCES_DIR = TASK_DIR / "references"
REGISTRY_PATH = REFERENCES_DIR / "home-registry.json"
STATE_ROOT = Path.home() / ".claude" / "skill-improvement"
RUNS_DIR = STATE_ROOT / "runs"
BACKUPS_DIR = STATE_ROOT / "backups"
RESULTS_PATH = STATE_ROOT / "results.tsv"
CHANGELOG_PATH = STATE_ROOT / "changelog.md"
CLAUDE_MD_PATH = Path.home() / "CLAUDE.md"

RUBRIC_ORDER = [
    "structure",
    "cso",
    "prose",
    "references",
    "claude_sync",
    "error_handling",
]

WEAK_ENDINGS = {
    "is",
    "are",
    "was",
    "were",
    "it",
    "that",
    "this",
    "these",
    "those",
    "why",
    "who",
    "which",
}
WEAK_OPENINGS = (
    "there is",
    "there are",
    "it is",
    "this is",
)
REDUNDANT_PHRASES = (
    "in order to",
    "at this point in time",
    "for the purpose of",
    "the fact that",
    "start to",
    "begin to",
)
QUALIFIERS = ("very", "really", "basically", "just", "quite", "extremely")
FALLBACK_KEYWORDS = (
    "fallback",
    "continue",
    "skip",
    "if",
    "missing",
    "not available",
    "fails",
    "failure",
    "disconnected",
)
GUARD_RAIL_KEYWORDS = ("do not", "never", "confirm", "validate", "verify")
MOJIBAKE_RE = re.compile(
    r"(?:\u00e2|\u00c3|\ufffd|"
    r"\u00e2\u20ac|\u00e2\u2020|"
    r"\u00e2\u20ac\u201d|\u00e2\u20ac\u201c|"
    r"\u00e2\u20ac\u0153|\u00e2\u20ac\ufffd|"
    r"\u00e2\u20ac\u02dc|\u00e2\u20ac\u2122)"
)
PATH_TOKEN_RE = re.compile(r"`([^`\n]+)`")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PLACEHOLDER_RE = re.compile(r"(\{.+?\}|\[.+?\]|YYYY|MM|DD|<.+?>)")
COMMAND_PREFIX_RE = re.compile(r"^\s*([A-Za-z0-9_.\\/-]+)")


@dataclass
class SkillRecord:
    skill_name: str
    skill_path: str
    home_id: str
    mode: str
    registry_target: str | None
    skill_type: str


def now_local() -> datetime:
    return datetime.now().astimezone()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def normalize_path_token(token: str) -> str:
    return token.replace("\\", "/")


def expand_user_path(token: str) -> Path:
    return Path(token.replace("~", str(Path.home()), 1)).expanduser()


def load_registry() -> dict[str, Any]:
    return load_json(REGISTRY_PATH)


def is_excluded(path: Path, patterns: list[str]) -> bool:
    normalized = normalize_path_token(str(path))
    for pattern in patterns:
        core = pattern.replace("**", "").strip("/")
        if core and core in normalized:
            return True
    return False


def discover_skills() -> list[SkillRecord]:
    registry = load_registry()
    records: list[SkillRecord] = []
    seen: set[str] = set()
    for home in registry["homes"]:
        for root_token in home["roots"]:
            root = expand_user_path(root_token)
            if not root.exists():
                continue
            for skill_md in root.rglob("SKILL.md"):
                if is_excluded(skill_md, home.get("exclude_patterns", [])):
                    continue
                normalized = str(skill_md.resolve()).lower()
                if normalized in seen:
                    continue
                seen.add(normalized)
                mode = "exclude" if skill_md.parent.name == "autoskill" else home["mode"]
                records.append(
                    SkillRecord(
                        skill_name=skill_md.parent.name,
                        skill_path=str(skill_md.resolve()),
                        home_id=home["home_id"],
                        mode=mode,
                        registry_target=home.get("registry_target"),
                        skill_type="scheduled_task" if "scheduled-tasks" in normalized else "skill",
                    )
                )
    records.sort(key=lambda item: (item.mode, item.home_id, item.skill_name, item.skill_path))
    return records


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    raw = match.group(1)
    metadata: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, text[match.end() :]


def strip_code_blocks(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]+`", " ", text)
    return text


def tokenize_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'/.-]*", text)


def sentence_sample(body: str) -> list[str]:
    cleaned = strip_code_blocks(body)
    return [chunk.strip() for chunk in SENTENCE_RE.split(cleaned) if chunk.strip()][:10]


def heading_levels(body: str) -> list[int]:
    return [len(match.group(1)) for match in HEADING_RE.finditer(body)]


def has_consistent_heading_hierarchy(body: str) -> bool:
    levels = heading_levels(body)
    if not levels:
        return False
    previous = levels[0]
    for level in levels[1:]:
        if level - previous > 1:
            return False
        previous = level
    return True


def looks_like_local_path(token: str) -> bool:
    if "://" in token:
        return False
    if PLACEHOLDER_RE.search(token):
        return False
    if token.startswith("~") or re.match(r"^[A-Za-z]:\\", token):
        return True
    if "/" in token or "\\" in token:
        return True
    return token.endswith((".md", ".json", ".yaml", ".yml", ".py", ".tsv"))


def resolve_local_path(token: str, skill_path: Path) -> tuple[str, Path | None]:
    if PLACEHOLDER_RE.search(token):
        return "unverifiable", None
    if token.startswith("~"):
        return "local", expand_user_path(token)
    if re.match(r"^[A-Za-z]:\\", token):
        return "local", Path(token)
    return "local", (skill_path.parent / token).resolve()


def extract_local_path_tokens(text: str) -> list[str]:
    return sorted({token for token in PATH_TOKEN_RE.findall(text) if looks_like_local_path(token)})


def extract_skill_refs(text: str) -> list[str]:
    refs = re.findall(r"`([a-z0-9][a-z0-9-]{1,63})`\s+skill", text)
    refs.extend(re.findall(r"\b([a-z0-9][a-z0-9-]{1,63})\s+skill\b", text))
    refs.extend(re.findall(r"(?:^|\s)/([a-z0-9][a-z0-9-]{1,63})(?=\s|$|[.,;:!?)])", text))
    return sorted(set(refs))


def extract_command_candidates(text: str) -> list[str]:
    commands: set[str] = set()
    for fence in re.findall(r"```(?:[A-Za-z0-9_-]+)?\n(.*?)```", text, flags=re.DOTALL):
        for line in fence.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or PLACEHOLDER_RE.search(stripped):
                continue
            match = COMMAND_PREFIX_RE.match(stripped)
            if match:
                candidate = Path(match.group(1)).name
                if candidate in {"-", "|"} or not re.search(r"[A-Za-z0-9]", candidate):
                    continue
                commands.add(candidate)
    return sorted(commands)


def parse_claude_skill_table() -> dict[str, dict[str, str]]:
    if not CLAUDE_MD_PATH.exists():
        return {}
    lines = CLAUDE_MD_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    header_index = None
    for index, line in enumerate(lines):
        if line.strip().startswith("| Skill | Status | Trigger | Purpose |"):
            header_index = index
            break
    if header_index is None:
        return {}
    rows: dict[str, dict[str, str]] = {}
    for line in lines[header_index + 2 :]:
        if not line.strip().startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4:
            continue
        rows[cells[0].strip("`")] = {
            "skill": cells[0],
            "status": cells[1],
            "trigger": cells[2],
            "purpose": cells[3],
        }
    return rows


def significant_words(text: str) -> set[str]:
    return {
        word
        for word in re.findall(r"[a-z0-9-]+", text.lower())
        if len(word) > 3 and word not in {"when", "also", "with", "this", "that", "from", "into"}
    }


def score_structure(metadata: dict[str, str], body: str, skill_type: str) -> int:
    score = 0
    if metadata.get("name") and metadata.get("description"):
        score += 4
    if SKILL_NAME_RE.match(metadata.get("name", "")):
        score += 2
    if re.search(r"^##\s+(overview|purpose)\b", body, flags=re.MULTILINE | re.IGNORECASE):
        score += 3
    if metadata.get("description", "").lower().startswith("use when") or re.search(
        r"^##\s+when to use\b", body, flags=re.MULTILINE | re.IGNORECASE
    ):
        score += 3
    lowered = body.lower()
    if "common mistakes" in lowered or "error handling" in lowered:
        score += 3
    word_count = len(tokenize_words(body))
    limit = 1500 if skill_type == "scheduled_task" else 3000
    if word_count <= limit:
        score += 3
    if has_consistent_heading_hierarchy(body):
        score += 2
    return min(score, 20)


def score_cso(metadata: dict[str, str], body: str) -> int:
    description = metadata.get("description", "")
    lowered = description.lower()
    score = 0
    if lowered.startswith("use when") or lowered.startswith("use this skill when"):
        score += 5
    workflow_verbs = ("score", "re-score", "backup", "revert", "log", "sync", "loop", "discover")
    if not any(verb in lowered for verb in workflow_verbs):
        score += 4
    if not re.search(r"\b(i|me|my|you|your)\b", lowered):
        score += 3
    if len(description) <= 500:
        score += 3
    if any(marker in description for marker in ('"', "'", ",")) or "asks" in lowered or "trigger" in lowered:
        score += 3
    if len(significant_words(description) & significant_words(body)) >= 2:
        score += 2
    return min(score, 20)


def score_prose(body: str) -> int:
    sentences = sentence_sample(body)
    if not sentences:
        return 0
    score = 0
    strong_endings = 0
    low_adverb_count = 0
    low_weak_opening_count = 0
    lengths: list[int] = []
    filler_hits = 0
    for sentence in sentences:
        words = tokenize_words(sentence.lower())
        if not words:
            continue
        lengths.append(len(words))
        if words[-1] not in WEAK_ENDINGS:
            strong_endings += 1
        if not any(re.search(rf"\b{qualifier}\b", sentence.lower()) for qualifier in QUALIFIERS) and not re.search(
            r"\b\w+ly\b", sentence.lower()
        ):
            low_adverb_count += 1
        if not sentence.lower().startswith(WEAK_OPENINGS):
            low_weak_opening_count += 1
        filler_hits += sum(sentence.lower().count(phrase) for phrase in REDUNDANT_PHRASES)
    total = max(len(lengths), 1)
    if strong_endings / total >= 0.6:
        score += 4
    if low_adverb_count / total >= 0.7:
        score += 3
    if filler_hits == 0:
        score += 3
    if low_weak_opening_count / total >= 0.8:
        score += 2
    if lengths and (max(lengths) - min(lengths) >= 6):
        score += 2
    average_length = sum(lengths) / total if lengths else 0
    if 6 <= average_length <= 26 and filler_hits <= 1:
        score += 4
    if not MOJIBAKE_RE.search(body):
        score += 2
    return min(score, 20)


def score_references(text: str, skill_path: Path, known_skill_names: set[str]) -> tuple[int, list[str]]:
    score = 0
    notes: list[str] = []
    broken_paths: list[str] = []
    for token in extract_local_path_tokens(text):
        category, resolved = resolve_local_path(token, skill_path)
        if category == "unverifiable":
            notes.append(f"unverifiable path: {token}")
            continue
        if resolved is None or not resolved.exists():
            broken_paths.append(token)
    if not broken_paths:
        score += 8
    else:
        notes.extend(f"missing path: {token}" for token in broken_paths)

    broken_skill_refs = [ref for ref in extract_skill_refs(text) if ref not in known_skill_names and ref != "autoskill"]
    if not broken_skill_refs:
        score += 6
    else:
        notes.extend(f"missing skill ref: {ref}" for ref in broken_skill_refs)

    broken_commands: list[str] = []
    allowed_commands = {
        "python",
        "uv",
        "git",
        "grep",
        "wc",
        "echo",
        "ls",
        "cat",
        "mkdir",
        "cp",
        "mv",
        "rm",
        "powershell",
        "pwsh",
        "get-content",
        "write-output",
    }
    for command in extract_command_candidates(text):
        if command.lower() in allowed_commands:
            continue
        if which(command) is None and which(f"{command}.exe") is None:
            broken_commands.append(command)
    if not broken_commands:
        score += 6
    else:
        notes.extend(f"missing command: {command}" for command in broken_commands)
    return min(score, 20), notes


def score_claude_sync(metadata: dict[str, str], skill_name: str, home_id: str) -> tuple[int, list[str]]:
    if not home_id.startswith("claude-"):
        return 20, [f"sync skipped for audit-only home: {home_id}"]
    rows = parse_claude_skill_table()
    row = rows.get(skill_name)
    score = 0
    notes: list[str] = []
    if row:
        score += 10
        if row["status"] in {"Built", "WIP", "Planned"}:
            score += 5
        else:
            notes.append(f"unknown status in CLAUDE.md: {row['status']}")
        if len(significant_words(row["purpose"]) & significant_words(metadata.get("description", ""))) >= 2:
            score += 5
        else:
            notes.append("CLAUDE.md purpose drift")
    else:
        notes.append("skill missing from CLAUDE.md")
    return min(score, 20), notes


def score_error_handling(body: str) -> int:
    lowered = body.lower()
    score = 0
    if "error handling" in lowered or "common mistakes" in lowered:
        score += 7
    if any(keyword in lowered for keyword in FALLBACK_KEYWORDS):
        score += 7
    if any(keyword in lowered for keyword in GUARD_RAIL_KEYWORDS):
        score += 6
    return min(score, 20)


def score_skill(path: Path, home_id: str, skill_type: str, known_skill_names: set[str]) -> dict[str, Any]:
    text = read_text(path)
    metadata, body = parse_frontmatter(text)
    reference_score, reference_notes = score_references(text, path, known_skill_names)
    claude_sync_score, claude_sync_notes = score_claude_sync(metadata, path.parent.name, home_id)
    scores = {
        "structure": score_structure(metadata, body, skill_type),
        "cso": score_cso(metadata, body),
        "prose": score_prose(body),
        "references": reference_score,
        "claude_sync": claude_sync_score,
        "error_handling": score_error_handling(body),
    }
    scores["total"] = sum(scores[dimension] for dimension in RUBRIC_ORDER)
    return {
        "metadata": metadata,
        "scores": scores,
        "notes": {
            "references": reference_notes,
            "claude_sync": claude_sync_notes,
        },
        "word_count": len(tokenize_words(body)),
    }


def ensure_state_dirs() -> None:
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)


def migrate_results_if_needed() -> None:
    ensure_state_dirs()
    header = "timestamp\trun_tag\tskill_path\thome_id\tdimension\tscore_before\tscore_after\tstatus\tchange_note\n"
    if not RESULTS_PATH.exists():
        write_text(RESULTS_PATH, header)
        return
    text = read_text(RESULTS_PATH)
    if text.startswith(header):
        return
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        write_text(RESULTS_PATH, header)
        return
    legacy_header = lines[0].split("\t")
    if legacy_header[:6] != ["date", "skill_path", "dimension", "score_before", "score_after", "status"]:
        raise RuntimeError(f"Unsupported results.tsv header: {legacy_header}")
    migrated = [header.rstrip("\n")]
    for row in lines[1:]:
        cells = row.split("\t")
        if len(cells) < 7:
            continue
        migrated.append(
            "\t".join(
                [
                    f"{cells[0]}T00:00:00",
                    "legacy",
                    cells[1],
                    "",
                    cells[2].replace("error-handling", "error_handling"),
                    cells[3],
                    cells[4],
                    cells[5],
                    cells[6],
                ]
            )
        )
    write_text(RESULTS_PATH, "\n".join(migrated) + "\n")


def ensure_changelog() -> None:
    if CHANGELOG_PATH.exists():
        return
    write_text(
        CHANGELOG_PATH,
        "# Autoskill Changelog\n\nAutoresearch-style improvements to SKILL.md files. Most recent first.\n",
    )


def create_run_tag() -> str:
    return now_local().strftime("autoskill-%Y%m%d-%H%M")


def run_dir(run_tag: str) -> Path:
    return RUNS_DIR / run_tag


def manifest_path(run_tag: str) -> Path:
    return run_dir(run_tag) / "manifest.json"


def inventory_path(run_tag: str) -> Path:
    return run_dir(run_tag) / "inventory.md"


def baseline_path(run_tag: str) -> Path:
    return run_dir(run_tag) / "baseline.tsv"


def experiments_path(run_tag: str) -> Path:
    return run_dir(run_tag) / "experiments.tsv"


def summary_path(run_tag: str) -> Path:
    return run_dir(run_tag) / "summary.md"


def current_scores_path(run_tag: str) -> Path:
    return run_dir(run_tag) / "current-scores.json"


def active_experiment_path(run_tag: str) -> Path:
    return run_dir(run_tag) / "active-experiment.json"


def diff_dir(run_tag: str) -> Path:
    return run_dir(run_tag) / "diffs"


def load_manifest(run_tag: str) -> dict[str, Any]:
    path = manifest_path(run_tag)
    if not path.exists():
        raise FileNotFoundError(f"Run manifest not found: {path}")
    return load_json(path)


def save_manifest(run_tag: str, manifest: dict[str, Any]) -> None:
    write_json(manifest_path(run_tag), manifest)


def inventory_markdown(records: list[SkillRecord]) -> str:
    lines = [
        f"# Autoskill Inventory - {now_local().strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "",
        "| # | Skill | Path | Home | Mode | Type |",
        "|---|-------|------|------|------|------|",
    ]
    for index, record in enumerate(records, start=1):
        lines.append(
            f"| {index} | {record.skill_name} | `{record.skill_path}` | {record.home_id} | {record.mode} | {record.skill_type} |"
        )
    return "\n".join(lines) + "\n"


def write_baseline(run_tag: str, rows: list[dict[str, Any]]) -> None:
    lines = [
        "skill_path\thome_id\tmode\tstructure\tcso\tprose\treferences\tclaude_sync\terror_handling\ttotal"
    ]
    for row in rows:
        scores = row["scores"]
        lines.append(
            "\t".join(
                [
                    row["skill_path"],
                    row["home_id"],
                    row["mode"],
                    str(scores["structure"]),
                    str(scores["cso"]),
                    str(scores["prose"]),
                    str(scores["references"]),
                    str(scores["claude_sync"]),
                    str(scores["error_handling"]),
                    str(scores["total"]),
                ]
            )
        )
    write_text(baseline_path(run_tag), "\n".join(lines) + "\n")


def append_tsv_row(path: Path, row: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="") as handle:
        handle.write("\t".join(row) + "\n")


def skill_backup_path(skill_name: str) -> Path:
    return BACKUPS_DIR / f"{skill_name}.SKILL.md.bak"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_next_target(current_scores: dict[str, Any], eligible_paths: set[str]) -> tuple[str, str, int] | None:
    candidates: list[tuple[int, int, str, str]] = []
    for skill_path, row in current_scores.items():
        if skill_path not in eligible_paths:
            continue
        for order, dimension in enumerate(RUBRIC_ORDER):
            candidates.append((row["scores"][dimension], order, skill_path, dimension))
    if not candidates:
        return None
    score_value, _, skill_path, dimension = min(candidates, key=lambda item: (item[0], item[1], item[2]))
    return skill_path, dimension, score_value


def shorten_description_for_purpose(description: str) -> str:
    text = re.sub(r"^Use when\s+", "", description, flags=re.IGNORECASE).strip()
    if len(text) <= 100:
        return text
    return text[:97].rstrip() + "..."


def derive_trigger(description: str, skill_type: str) -> str:
    phrases = re.findall(r'"([^"]+)"', description)
    if phrases:
        return ", ".join(f'"{phrase}"' for phrase in phrases[:3])
    if skill_type == "scheduled_task":
        return "Scheduled task"
    return "See SKILL.md"


def sync_claude_md(records: list[SkillRecord]) -> dict[str, int]:
    if not CLAUDE_MD_PATH.exists():
        raise FileNotFoundError(f"CLAUDE.md not found at {CLAUDE_MD_PATH}")
    lines = CLAUDE_MD_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    table_start = None
    header_index = None
    for index, line in enumerate(lines):
        if line.strip() == "### Skills":
            table_start = index
        if table_start is not None and line.strip().startswith("| Skill | Status | Trigger | Purpose |"):
            header_index = index
            break
    if table_start is None or header_index is None:
        raise RuntimeError("Could not locate the Skills table in CLAUDE.md")

    table_end = None
    for index in range(header_index + 2, len(lines)):
        if not lines[index].strip().startswith("|"):
            table_end = index
            break
    if table_end is None:
        table_end = len(lines)

    row_map = parse_claude_skill_table()
    updated = 0
    added = 0
    new_rows: list[str] = []
    for record in records:
        metadata, _ = parse_frontmatter(read_text(Path(record.skill_path)))
        purpose = shorten_description_for_purpose(metadata.get("description", ""))
        trigger = derive_trigger(metadata.get("description", ""), record.skill_type)
        desired_line = f"| `{record.skill_name}` | Built | {trigger} | {purpose} |"
        if record.skill_name in row_map:
            for index in range(header_index + 2, table_end):
                if lines[index].strip().startswith(f"| `{record.skill_name}` |"):
                    cells = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
                    current_status = cells[1] if len(cells) > 1 else "Built"
                    current_trigger = cells[2] if len(cells) > 2 else trigger
                    candidate_line = f"| `{record.skill_name}` | {current_status} | {current_trigger} | {purpose} |"
                    if lines[index] != candidate_line:
                        lines[index] = candidate_line
                        updated += 1
                    break
        else:
            new_rows.append(desired_line)
            added += 1

    if new_rows:
        lines[table_end:table_end] = new_rows
    write_text(CLAUDE_MD_PATH, "\n".join(lines) + "\n")
    return {"added": added, "updated": updated}


def command_discover(_: argparse.Namespace) -> int:
    records = discover_skills()
    print(json.dumps({"count": len(records), "records": [asdict(record) for record in records]}, indent=2))
    return 0


def command_score_skill(args: argparse.Namespace) -> int:
    records = discover_skills()
    known_skill_names = {record.skill_name for record in records}
    target = Path(args.skill_path).expanduser().resolve()
    match = next((record for record in records if Path(record.skill_path) == target), None)
    home_id = match.home_id if match else "ad_hoc"
    skill_type = match.skill_type if match else "skill"
    payload = score_skill(target, home_id, skill_type, known_skill_names)
    payload["skill_path"] = str(target)
    payload["home_id"] = home_id
    payload["skill_type"] = skill_type
    print(json.dumps(payload, indent=2))
    return 0


def command_init_run(args: argparse.Namespace) -> int:
    ensure_state_dirs()
    migrate_results_if_needed()
    ensure_changelog()
    records = discover_skills()
    run_tag = args.run_tag or create_run_tag()
    run_root = run_dir(run_tag)
    run_root.mkdir(parents=True, exist_ok=False)
    known_skill_names = {record.skill_name for record in records}

    score_rows: list[dict[str, Any]] = []
    current_scores: dict[str, Any] = {}
    eligible_targets: list[dict[str, Any]] = []
    audit_only_targets: list[dict[str, Any]] = []
    for record in records:
        scored = score_skill(Path(record.skill_path), record.home_id, record.skill_type, known_skill_names)
        row = {
            "skill_name": record.skill_name,
            "skill_path": record.skill_path,
            "home_id": record.home_id,
            "mode": record.mode,
            "skill_type": record.skill_type,
            "scores": scored["scores"],
            "notes": scored["notes"],
            "word_count": scored["word_count"],
        }
        score_rows.append(row)
        current_scores[record.skill_path] = row
        target_stub = {
            "skill_name": record.skill_name,
            "skill_path": record.skill_path,
            "home_id": record.home_id,
            "skill_type": record.skill_type,
        }
        if record.mode == "mutate":
            eligible_targets.append(target_stub)
        elif record.mode == "audit_only":
            audit_only_targets.append(target_stub)

    started_at = now_local()
    deadline_at = started_at + timedelta(minutes=args.budget_minutes)
    manifest = {
        "run_tag": run_tag,
        "started_at": started_at.isoformat(),
        "deadline_at": deadline_at.isoformat(),
        "budget_minutes": args.budget_minutes,
        "eligible_targets": eligible_targets,
        "audit_only_targets": audit_only_targets,
        "kept": 0,
        "reverted": 0,
        "unchanged": 0,
        "errors": 0,
        "sync_warnings": [],
    }
    save_manifest(run_tag, manifest)
    write_text(inventory_path(run_tag), inventory_markdown(records))
    write_baseline(run_tag, score_rows)
    write_json(current_scores_path(run_tag), current_scores)
    write_text(
        experiments_path(run_tag),
        "timestamp\trun_tag\tskill_path\thome_id\tdimension\tscore_before\tscore_after\tstatus\tchange_note\n",
    )
    print(
        json.dumps(
            {
                "run_tag": run_tag,
                "eligible_count": len(eligible_targets),
                "audit_only_count": len(audit_only_targets),
                "deadline_at": deadline_at.isoformat(),
            },
            indent=2,
        )
    )
    return 0


def command_start_experiment(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.run_tag)
    if now_local() >= datetime.fromisoformat(manifest["deadline_at"]):
        print(json.dumps({"status": "time_expired", "run_tag": args.run_tag}, indent=2))
        return 0
    active_path = active_experiment_path(args.run_tag)
    if active_path.exists():
        raise RuntimeError(f"Active experiment already exists for run {args.run_tag}")

    current_scores = load_json(current_scores_path(args.run_tag))
    eligible_paths = {item["skill_path"] for item in manifest["eligible_targets"]}
    selected = select_next_target(current_scores, eligible_paths)
    if selected is None:
        print(json.dumps({"status": "no_targets", "run_tag": args.run_tag}, indent=2))
        return 0

    skill_path_str, dimension, score_before = selected
    skill_path = Path(skill_path_str)
    backup_path = skill_backup_path(skill_path.parent.name)
    shutil.copy2(skill_path, backup_path)
    experiment = {
        "run_tag": args.run_tag,
        "skill_name": skill_path.parent.name,
        "skill_path": skill_path_str,
        "home_id": current_scores[skill_path_str]["home_id"],
        "dimension": dimension,
        "score_before": score_before,
        "started_at": now_local().isoformat(),
        "backup_path": str(backup_path),
        "pre_hash": file_hash(skill_path),
    }
    write_json(active_path, experiment)
    print(json.dumps(experiment, indent=2))
    return 0


def command_evaluate_change(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.run_tag)
    active_path = active_experiment_path(args.run_tag)
    if not active_path.exists():
        raise FileNotFoundError(f"No active experiment found for run {args.run_tag}")

    experiment = load_json(active_path)
    skill_path = Path(experiment["skill_path"])
    backup_path = Path(experiment["backup_path"])
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup not found for active experiment: {backup_path}")

    records = discover_skills()
    known_skill_names = {record.skill_name for record in records}
    record = next(item for item in records if item.skill_path == experiment["skill_path"])
    scored_after = score_skill(skill_path, record.home_id, record.skill_type, known_skill_names)
    attempted_score = scored_after["scores"][experiment["dimension"]]
    current_text = read_text(skill_path)
    backup_text = read_text(backup_path)

    if attempted_score > experiment["score_before"]:
        status = "improved"
        final_scores = scored_after
        manifest["kept"] += 1
    else:
        status = "unchanged" if attempted_score == experiment["score_before"] else "reverted"
        shutil.copy2(backup_path, skill_path)
        final_scores = score_skill(skill_path, record.home_id, record.skill_type, known_skill_names)
        manifest["unchanged" if status == "unchanged" else "reverted"] += 1

    diff_path = diff_dir(args.run_tag) / (
        f"{now_local().strftime('%Y%m%d-%H%M%S')}-{skill_path.parent.name}-{experiment['dimension']}.diff"
    )
    diff = "".join(
        difflib.unified_diff(
            backup_text.splitlines(keepends=True),
            current_text.splitlines(keepends=True),
            fromfile=str(backup_path),
            tofile=str(skill_path),
        )
    )
    write_text(diff_path, diff if diff else "# No textual diff captured.\n")

    current_scores = load_json(current_scores_path(args.run_tag))
    current_scores[experiment["skill_path"]]["scores"] = final_scores["scores"]
    current_scores[experiment["skill_path"]]["notes"] = final_scores["notes"]
    current_scores[experiment["skill_path"]]["word_count"] = final_scores["word_count"]
    write_json(current_scores_path(args.run_tag), current_scores)

    timestamp = now_local().isoformat(timespec="seconds")
    row = [
        timestamp,
        args.run_tag,
        experiment["skill_path"],
        experiment["home_id"],
        experiment["dimension"],
        str(experiment["score_before"]),
        str(attempted_score),
        status,
        args.change_note,
    ]
    append_tsv_row(experiments_path(args.run_tag), row)
    append_tsv_row(RESULTS_PATH, row)
    save_manifest(args.run_tag, manifest)
    active_path.unlink()

    print(
        json.dumps(
            {
                "status": status,
                "skill_path": experiment["skill_path"],
                "dimension": experiment["dimension"],
                "score_before": experiment["score_before"],
                "score_after": attempted_score,
                "diff_path": str(diff_path),
                "post_hash": file_hash(skill_path),
            },
            indent=2,
        )
    )
    return 0


def command_sync_registry(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.run_tag)
    records = discover_skills()
    claude_records = [record for record in records if record.home_id.startswith("claude-")]
    sync_result = sync_claude_md(claude_records)
    audit_warnings = [
        f"{record.home_id}: audit-only sync skipped for {record.skill_name}"
        for record in records
        if record.mode == "audit_only"
    ]
    manifest["sync_warnings"] = audit_warnings
    save_manifest(args.run_tag, manifest)
    print(
        json.dumps(
            {
                "run_tag": args.run_tag,
                "updated": sync_result["updated"],
                "added": sync_result["added"],
                "audit_warnings": len(audit_warnings),
            },
            indent=2,
        )
    )
    return 0


def parse_experiment_rows(run_tag: str) -> list[dict[str, str]]:
    path = experiments_path(run_tag)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def command_finalize_run(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.run_tag)
    rows = parse_experiment_rows(args.run_tag)
    kept = sum(1 for row in rows if row["status"] == "improved")
    unchanged = sum(1 for row in rows if row["status"] == "unchanged")
    reverted = sum(1 for row in rows if row["status"] == "reverted")
    errors = manifest.get("errors", 0)
    audit_warnings = manifest.get("sync_warnings", [])

    summary_lines = [
        f"# Autoskill Summary - {args.run_tag}",
        "",
        f"- Started: {manifest['started_at']}",
        f"- Deadline: {manifest['deadline_at']}",
        f"- Budget minutes: {manifest['budget_minutes']}",
        f"- Eligible targets: {len(manifest['eligible_targets'])}",
        f"- Audit-only targets: {len(manifest['audit_only_targets'])}",
        f"- Improvements kept: {kept}",
        f"- Reverted: {reverted}",
        f"- Unchanged: {unchanged}",
        f"- Errors: {errors}",
        "",
        "## Experiments",
        "",
        "| Skill | Dimension | Before | After | Status | Change |",
        "|-------|-----------|--------|-------|--------|--------|",
    ]
    for row in rows:
        summary_lines.append(
            f"| `{Path(row['skill_path']).parent.name}` | {row['dimension']} | {row['score_before']} | {row['score_after']} | {row['status']} | {row['change_note']} |"
        )
    if audit_warnings:
        summary_lines.extend(["", "## Audit Warnings", ""])
        summary_lines.extend(f"- {warning}" for warning in audit_warnings[:20])
    write_text(summary_path(args.run_tag), "\n".join(summary_lines) + "\n")

    changelog_lines = [
        "",
        f"## {now_local().strftime('%Y-%m-%d')} ({args.run_tag})",
        "",
        f"**Skills scanned:** {len(manifest['eligible_targets']) + len(manifest['audit_only_targets'])}",
        f"**Improvements kept:** {kept}",
        f"**Reverted:** {reverted}",
        f"**Unchanged:** {unchanged}",
        f"**Errors:** {errors}",
        "",
        "| Skill | Dimension | Before | After | Status | Change |",
        "|-------|-----------|--------|-------|--------|--------|",
    ]
    for row in rows:
        changelog_lines.append(
            f"| {Path(row['skill_path']).parent.name} | {row['dimension']} | {row['score_before']} | {row['score_after']} | {row['status']} | {row['change_note']} |"
        )
    if audit_warnings:
        changelog_lines.extend(["", "**Audit warnings:**"])
        changelog_lines.extend(f"- {warning}" for warning in audit_warnings[:10])
    with CHANGELOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(changelog_lines) + "\n")

    manifest["ended_at"] = now_local().isoformat()
    manifest["kept"] = kept
    manifest["reverted"] = reverted
    manifest["unchanged"] = unchanged
    manifest["errors"] = errors
    save_manifest(args.run_tag, manifest)

    print(
        f"Autoskill complete: {len(manifest['eligible_targets']) + len(manifest['audit_only_targets'])} scanned, {kept} improved, {reverted} reverted, {unchanged} unchanged, {errors} errors"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Autoresearch-style autoskill controller")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("discover")

    score_parser = subparsers.add_parser("score-skill")
    score_parser.add_argument("--skill-path", required=True)

    init_parser = subparsers.add_parser("init-run")
    init_parser.add_argument("--budget-minutes", type=int, default=30)
    init_parser.add_argument("--run-tag")

    start_parser = subparsers.add_parser("start-experiment")
    start_parser.add_argument("--run-tag", required=True)

    evaluate_parser = subparsers.add_parser("evaluate-change")
    evaluate_parser.add_argument("--run-tag", required=True)
    evaluate_parser.add_argument("--change-note", required=True)

    sync_parser = subparsers.add_parser("sync-registry")
    sync_parser.add_argument("--run-tag", required=True)

    finalize_parser = subparsers.add_parser("finalize-run")
    finalize_parser.add_argument("--run-tag", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    commands = {
        "discover": command_discover,
        "score-skill": command_score_skill,
        "init-run": command_init_run,
        "start-experiment": command_start_experiment,
        "evaluate-change": command_evaluate_change,
        "sync-registry": command_sync_registry,
        "finalize-run": command_finalize_run,
    }
    try:
        return commands[args.command](args)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": str(exc), "command": args.command}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
