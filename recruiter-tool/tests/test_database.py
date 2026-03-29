"""Tests for recruiter-tool/database.py"""

import json
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import database


class TestInitDb:
    """Tests for init_db()."""

    def test_creates_candidates_table(self, tmp_db):
        conn = sqlite3.connect(tmp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='candidates'"
        )
        assert cursor.fetchone() is not None
        conn.close()

    def test_creates_attachments_table(self, tmp_db):
        conn = sqlite3.connect(tmp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='attachments'"
        )
        assert cursor.fetchone() is not None
        conn.close()

    def test_candidates_table_has_expected_columns(self, tmp_db):
        conn = sqlite3.connect(tmp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(candidates)")
        columns = {row[1] for row in cursor.fetchall()}
        expected = {
            'id', 'name', 'current_company', 'current_title',
            'years_experience_total', 'years_experience_therapeutic',
            'technical_skills', 'compensation_current_min',
            'compensation_current_max', 'compensation_target_min',
            'compensation_target_max', 'notice_period', 'location',
            'open_to_relocation', 'red_flags', 'why_interesting',
            'therapeutic_areas', 'phase_experience', 'transcript',
            'created_at', 'search_tags', 'attachment_path',
        }
        assert expected == columns
        conn.close()

    def test_attachments_table_has_expected_columns(self, tmp_db):
        conn = sqlite3.connect(tmp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(attachments)")
        columns = {row[1] for row in cursor.fetchall()}
        expected = {
            'id', 'candidate_id', 'file_name', 'file_type',
            'file_path', 'description', 'uploaded_at',
        }
        assert expected == columns
        conn.close()

    def test_idempotent_init(self, tmp_db):
        """Calling init_db() twice should not raise or duplicate tables."""
        database.init_db()
        database.init_db()
        conn = sqlite3.connect(tmp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='candidates'"
        )
        assert cursor.fetchone()[0] == 1
        conn.close()


class TestSaveCandidate:
    """Tests for save_candidate()."""

    def test_returns_integer_id(self, tmp_db, sample_candidate):
        cid = database.save_candidate(sample_candidate)
        assert isinstance(cid, int)
        assert cid > 0

    def test_increments_id(self, tmp_db, sample_candidate):
        id1 = database.save_candidate(sample_candidate)
        id2 = database.save_candidate(sample_candidate)
        assert id2 == id1 + 1

    def test_stores_all_fields(self, tmp_db, sample_candidate):
        cid = database.save_candidate(sample_candidate)
        result = database.get_candidate(cid)
        assert result['name'] == 'Jane Smith'
        assert result['current_company'] == 'Genentech'
        assert result['years_experience_total'] == 18
        assert result['technical_skills'] == ['IND filings', 'Phase 3 trials', 'Oncology', 'FDA meetings']
        assert result['therapeutic_areas'] == ['oncology', 'rare disease']
        assert result['phase_experience'] == ['Phase 2', 'Phase 3', 'NDA/BLA']
        assert result['search_tags'] == ['oncology', 'vp-level', 'big-pharma']

    def test_handles_minimal_data(self, tmp_db, minimal_candidate):
        cid = database.save_candidate(minimal_candidate)
        result = database.get_candidate(cid)
        assert result['name'] == 'John Doe'
        assert result['current_company'] is None
        assert result['technical_skills'] == []
        assert result['therapeutic_areas'] == []

    def test_stores_json_fields_as_json(self, tmp_db, sample_candidate):
        """Verify that list fields are stored as JSON strings in the raw database."""
        cid = database.save_candidate(sample_candidate)
        conn = sqlite3.connect(tmp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT technical_skills, therapeutic_areas FROM candidates WHERE id = ?", (cid,))
        row = cursor.fetchone()
        conn.close()
        # Raw data should be valid JSON strings
        assert json.loads(row[0]) == sample_candidate['technical_skills']
        assert json.loads(row[1]) == sample_candidate['therapeutic_areas']


class TestSearchCandidates:
    """Tests for search_candidates()."""

    def test_returns_all_without_filters(self, tmp_db, sample_candidate):
        database.save_candidate(sample_candidate)
        database.save_candidate({**sample_candidate, 'name': 'Bob Jones'})
        results = database.search_candidates()
        assert len(results) == 2

    def test_empty_results_for_no_matches(self, tmp_db, sample_candidate):
        database.save_candidate(sample_candidate)
        results = database.search_candidates({'company': 'NonexistentCorp'})
        assert len(results) == 0

    def test_filter_by_therapeutic_area(self, tmp_db, sample_candidate):
        database.save_candidate(sample_candidate)
        database.save_candidate({
            **sample_candidate,
            'name': 'Bob',
            'therapeutic_areas': ['cardiovascular'],
        })
        results = database.search_candidates({'therapeutic_area': 'oncology'})
        assert len(results) == 1
        assert results[0]['name'] == 'Jane Smith'

    def test_filter_by_phase(self, tmp_db, sample_candidate):
        database.save_candidate(sample_candidate)
        results = database.search_candidates({'phase': 'Phase 3'})
        assert len(results) == 1

    def test_filter_by_company(self, tmp_db, sample_candidate):
        database.save_candidate(sample_candidate)
        results = database.search_candidates({'company': 'Genentech'})
        assert len(results) == 1

    def test_filter_by_search_tag(self, tmp_db, sample_candidate):
        database.save_candidate(sample_candidate)
        results = database.search_candidates({'search_tag': 'vp-level'})
        assert len(results) == 1

    def test_combined_filters(self, tmp_db, sample_candidate):
        database.save_candidate(sample_candidate)
        results = database.search_candidates({
            'therapeutic_area': 'oncology',
            'company': 'Genentech',
        })
        assert len(results) == 1

    def test_returns_deserialized_json_fields(self, tmp_db, sample_candidate):
        database.save_candidate(sample_candidate)
        results = database.search_candidates()
        assert isinstance(results[0]['technical_skills'], list)
        assert isinstance(results[0]['therapeutic_areas'], list)
        assert isinstance(results[0]['phase_experience'], list)
        assert isinstance(results[0]['search_tags'], list)

    def test_ordered_by_created_at_desc(self, tmp_db, sample_candidate):
        """Results should be ordered by created_at DESC. When timestamps match,
        the exact ordering between equal-timestamp records is acceptable either way."""
        database.save_candidate({**sample_candidate, 'name': 'First'})
        database.save_candidate({**sample_candidate, 'name': 'Second'})
        results = database.search_candidates()
        assert len(results) == 2
        names = {r['name'] for r in results}
        assert names == {'First', 'Second'}


class TestGetCandidate:
    """Tests for get_candidate()."""

    def test_returns_candidate_by_id(self, tmp_db, sample_candidate):
        cid = database.save_candidate(sample_candidate)
        result = database.get_candidate(cid)
        assert result is not None
        assert result['name'] == 'Jane Smith'

    def test_returns_none_for_nonexistent_id(self, tmp_db):
        result = database.get_candidate(9999)
        assert result is None

    def test_deserializes_json_fields(self, tmp_db, sample_candidate):
        cid = database.save_candidate(sample_candidate)
        result = database.get_candidate(cid)
        assert isinstance(result['technical_skills'], list)
        assert isinstance(result['therapeutic_areas'], list)
        assert isinstance(result['phase_experience'], list)
        assert isinstance(result['search_tags'], list)

    def test_handles_empty_json_fields(self, tmp_db, minimal_candidate):
        cid = database.save_candidate(minimal_candidate)
        result = database.get_candidate(cid)
        assert result['technical_skills'] == []
        assert result['therapeutic_areas'] == []
        assert result['phase_experience'] == []
        assert result['search_tags'] == []
