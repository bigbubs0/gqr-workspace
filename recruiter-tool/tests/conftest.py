"""Shared fixtures for recruiter-tool tests."""

import os
import sys
import sqlite3
import tempfile
import pytest

# Add recruiter-tool directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    """Create a temporary SQLite database for testing."""
    db_path = str(tmp_path / 'test_candidates.db')
    import database
    import file_handler
    monkeypatch.setattr(database, 'DB_PATH', db_path)
    monkeypatch.setattr(file_handler, 'DB_PATH', db_path)
    database.init_db()
    return db_path


@pytest.fixture
def sample_candidate():
    """Return a complete sample candidate data dict."""
    return {
        'name': 'Jane Smith',
        'current_company': 'Genentech',
        'current_title': 'VP Clinical Development',
        'years_experience_total': 18,
        'years_experience_therapeutic': 12,
        'technical_skills': ['IND filings', 'Phase 3 trials', 'Oncology', 'FDA meetings'],
        'compensation_current_min': 280,
        'compensation_current_max': 320,
        'compensation_target_min': 350,
        'compensation_target_max': 400,
        'notice_period': '2 weeks',
        'location': 'South San Francisco, CA',
        'open_to_relocation': True,
        'red_flags': '',
        'why_interesting': 'Strong Genentech pedigree with deep oncology expertise. Led two NDA submissions. Building teams from scratch at scale.',
        'therapeutic_areas': ['oncology', 'rare disease'],
        'phase_experience': ['Phase 2', 'Phase 3', 'NDA/BLA'],
        'transcript': 'Sample transcript text for testing purposes.',
        'search_tags': ['oncology', 'vp-level', 'big-pharma'],
        'attachment_path': None,
    }


@pytest.fixture
def minimal_candidate():
    """Return a minimal candidate data dict with only required fields."""
    return {
        'name': 'John Doe',
    }


@pytest.fixture
def app_client(tmp_db):
    """Create a Flask test client with a temporary database."""
    import app as flask_app
    flask_app.app.config['TESTING'] = True
    with flask_app.app.test_client() as client:
        yield client
