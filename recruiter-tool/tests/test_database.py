"""Tests for the SQLite layer in database.py.

Covers schema initialization, candidate persistence, JSON-column round-tripping,
search filter combinations, and edge cases around missing fields.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta


def _make_candidate(**overrides) -> dict:
    base = {
        "name": "Jane Doe",
        "current_company": "Acme Bio",
        "current_title": "Director",
        "years_experience_total": 12,
        "years_experience_therapeutic": 8,
        "technical_skills": ["Phase 2", "FDA submissions"],
        "compensation_current_min": 200,
        "compensation_current_max": 220,
        "compensation_target_min": 240,
        "compensation_target_max": 260,
        "notice_period": "2 weeks",
        "location": "Boston, MA",
        "open_to_relocation": False,
        "red_flags": "",
        "why_interesting": "Strong fit.",
        "therapeutic_areas": ["oncology", "rare disease"],
        "phase_experience": ["Phase 2", "Phase 3"],
        "transcript": "Full interview transcript here.",
        "search_tags": ["VP Clinical"],
        "attachment_path": None,
    }
    base.update(overrides)
    return base


def test_init_db_creates_required_tables(app_stack):
    app_stack.database.init_db()
    conn = sqlite3.connect(app_stack.database.DB_PATH)
    try:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        conn.close()
    assert "candidates" in tables
    assert "attachments" in tables


def test_init_db_is_idempotent(app_stack):
    """Calling init_db twice must not raise or duplicate tables."""
    app_stack.database.init_db()
    app_stack.database.init_db()
    conn = sqlite3.connect(app_stack.database.DB_PATH)
    try:
        rows = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='candidates'").fetchone()
    finally:
        conn.close()
    assert rows[0] == 1


def test_save_candidate_returns_autoincrement_id(app_stack):
    db = app_stack.database
    db.init_db()
    first_id = db.save_candidate(_make_candidate())
    second_id = db.save_candidate(_make_candidate(name="John Smith"))
    assert isinstance(first_id, int)
    assert second_id == first_id + 1


def test_get_candidate_round_trips_list_columns(app_stack):
    """Lists stored as JSON should be returned as Python lists."""
    db = app_stack.database
    db.init_db()
    candidate_id = db.save_candidate(_make_candidate(
        technical_skills=["IND filings", "Phase 3"],
        therapeutic_areas=["oncology"],
        phase_experience=["Phase 2", "Phase 3", "NDA/BLA"],
        search_tags=["Aditum VP", "urgent"],
    ))
    candidate = db.get_candidate(candidate_id)
    assert candidate is not None
    assert candidate["technical_skills"] == ["IND filings", "Phase 3"]
    assert candidate["therapeutic_areas"] == ["oncology"]
    assert candidate["phase_experience"] == ["Phase 2", "Phase 3", "NDA/BLA"]
    assert candidate["search_tags"] == ["Aditum VP", "urgent"]


def test_get_candidate_returns_none_for_missing_id(app_stack):
    db = app_stack.database
    db.init_db()
    assert db.get_candidate(99999) is None


def test_get_candidate_handles_null_json_columns(app_stack):
    """If list fields are missing from the input dict, get_candidate must return [] not crash."""
    db = app_stack.database
    db.init_db()
    sparse = _make_candidate()
    for key in ("technical_skills", "therapeutic_areas", "phase_experience", "search_tags"):
        sparse.pop(key)
    candidate_id = db.save_candidate(sparse)
    candidate = db.get_candidate(candidate_id)
    assert candidate["technical_skills"] == []
    assert candidate["therapeutic_areas"] == []
    assert candidate["phase_experience"] == []
    assert candidate["search_tags"] == []


def test_search_with_no_filters_returns_all(app_stack):
    db = app_stack.database
    db.init_db()
    db.save_candidate(_make_candidate(name="Alice"))
    db.save_candidate(_make_candidate(name="Bob"))
    db.save_candidate(_make_candidate(name="Carol"))
    results = db.search_candidates()
    assert len(results) == 3


def test_search_with_empty_filters_returns_all(app_stack):
    db = app_stack.database
    db.init_db()
    db.save_candidate(_make_candidate(name="Alice"))
    results = db.search_candidates({})
    assert len(results) == 1


def test_search_filters_by_therapeutic_area(app_stack):
    db = app_stack.database
    db.init_db()
    db.save_candidate(_make_candidate(name="Onc", therapeutic_areas=["oncology"]))
    db.save_candidate(_make_candidate(name="Cardio", therapeutic_areas=["cardiovascular"]))
    results = db.search_candidates({"therapeutic_area": "oncology"})
    assert len(results) == 1
    assert results[0]["name"] == "Onc"


def test_search_filters_by_phase(app_stack):
    db = app_stack.database
    db.init_db()
    db.save_candidate(_make_candidate(name="EarlyPhase", phase_experience=["Phase 1"]))
    db.save_candidate(_make_candidate(name="LatePhase", phase_experience=["Phase 3", "NDA/BLA"]))
    results = db.search_candidates({"phase": "Phase 3"})
    assert len(results) == 1
    assert results[0]["name"] == "LatePhase"


def test_search_filters_by_company_uses_partial_match(app_stack):
    db = app_stack.database
    db.init_db()
    db.save_candidate(_make_candidate(name="A", current_company="Structure Therapeutics"))
    db.save_candidate(_make_candidate(name="B", current_company="Apogee"))
    results = db.search_candidates({"company": "Structure"})
    assert len(results) == 1
    assert results[0]["name"] == "A"


def test_search_filters_by_search_tag(app_stack):
    db = app_stack.database
    db.init_db()
    db.save_candidate(_make_candidate(name="X", search_tags=["Aditum VP"]))
    db.save_candidate(_make_candidate(name="Y", search_tags=["Apogee Biostats"]))
    results = db.search_candidates({"search_tag": "Aditum"})
    assert len(results) == 1
    assert results[0]["name"] == "X"


def test_search_combines_multiple_filters(app_stack):
    db = app_stack.database
    db.init_db()
    db.save_candidate(_make_candidate(name="Match", current_company="Acme", therapeutic_areas=["oncology"]))
    db.save_candidate(_make_candidate(name="WrongCompany", current_company="Beta", therapeutic_areas=["oncology"]))
    db.save_candidate(_make_candidate(name="WrongArea", current_company="Acme", therapeutic_areas=["cardiovascular"]))
    results = db.search_candidates({"company": "Acme", "therapeutic_area": "oncology"})
    assert len(results) == 1
    assert results[0]["name"] == "Match"


def test_search_returns_results_ordered_by_created_at_desc(app_stack):
    """Default CURRENT_TIMESTAMP has 1-second resolution, so we backdate
    explicitly to verify the ORDER BY clause does the right thing."""
    db = app_stack.database
    db.init_db()
    first_id = db.save_candidate(_make_candidate(name="First"))
    second_id = db.save_candidate(_make_candidate(name="Second"))
    third_id = db.save_candidate(_make_candidate(name="Third"))

    now = datetime.utcnow()
    conn = sqlite3.connect(db.DB_PATH)
    try:
        for cand_id, offset in ((first_id, 30), (second_id, 20), (third_id, 10)):
            backdate = (now - timedelta(minutes=offset)).isoformat(sep=" ", timespec="seconds")
            conn.execute("UPDATE candidates SET created_at = ? WHERE id = ?", (backdate, cand_id))
        conn.commit()
    finally:
        conn.close()

    results = db.search_candidates()
    assert [row["name"] for row in results] == ["Third", "Second", "First"]


def test_search_days_back_filter_respects_recency(app_stack):
    """Records older than the days_back window should be excluded."""
    db = app_stack.database
    db.init_db()
    # Insert one with a manually backdated created_at; one fresh.
    fresh_id = db.save_candidate(_make_candidate(name="Fresh"))
    old_id = db.save_candidate(_make_candidate(name="Old"))
    backdate = (datetime.utcnow() - timedelta(days=60)).isoformat(sep=" ", timespec="seconds")
    conn = sqlite3.connect(db.DB_PATH)
    try:
        conn.execute("UPDATE candidates SET created_at = ? WHERE id = ?", (backdate, old_id))
        conn.commit()
    finally:
        conn.close()

    recent = db.search_candidates({"days_back": "30"})
    names = {row["name"] for row in recent}
    assert "Fresh" in names
    assert "Old" not in names
    # And without the filter both come back.
    assert {row["name"] for row in db.search_candidates()} == {"Fresh", "Old"}
    _ = fresh_id


def test_save_candidate_preserves_boolean_relocation_flag(app_stack):
    db = app_stack.database
    db.init_db()
    yes_id = db.save_candidate(_make_candidate(name="WillMove", open_to_relocation=True))
    no_id = db.save_candidate(_make_candidate(name="Stay", open_to_relocation=False))
    assert db.get_candidate(yes_id)["open_to_relocation"] in (1, True)
    assert db.get_candidate(no_id)["open_to_relocation"] in (0, False)
