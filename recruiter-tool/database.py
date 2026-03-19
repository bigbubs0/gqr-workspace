import sqlite3
import json
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'candidates.db')

def init_db():
    """Initialize the database with required tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            current_company TEXT,
            current_title TEXT,
            years_experience_total INTEGER,
            years_experience_therapeutic INTEGER,
            technical_skills TEXT,
            compensation_current_min INTEGER,
            compensation_current_max INTEGER,
            compensation_target_min INTEGER,
            compensation_target_max INTEGER,
            notice_period TEXT,
            location TEXT,
            open_to_relocation BOOLEAN,
            red_flags TEXT,
            why_interesting TEXT,
            therapeutic_areas TEXT,
            phase_experience TEXT,
            transcript TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            search_tags TEXT,
            attachment_path TEXT
        )
    ''')

    # Create attachments table for multiple files per candidate
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT,
            file_path TEXT NOT NULL,
            description TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        )
    ''')

    conn.commit()
    conn.close()

def save_candidate(candidate_data):
    """Save a candidate to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO candidates (
            name, current_company, current_title, years_experience_total,
            years_experience_therapeutic, technical_skills, compensation_current_min,
            compensation_current_max, compensation_target_min, compensation_target_max,
            notice_period, location, open_to_relocation, red_flags, why_interesting,
            therapeutic_areas, phase_experience, transcript, search_tags, attachment_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        candidate_data.get('name'),
        candidate_data.get('current_company'),
        candidate_data.get('current_title'),
        candidate_data.get('years_experience_total'),
        candidate_data.get('years_experience_therapeutic'),
        json.dumps(candidate_data.get('technical_skills', [])),
        candidate_data.get('compensation_current_min'),
        candidate_data.get('compensation_current_max'),
        candidate_data.get('compensation_target_min'),
        candidate_data.get('compensation_target_max'),
        candidate_data.get('notice_period'),
        candidate_data.get('location'),
        candidate_data.get('open_to_relocation'),
        candidate_data.get('red_flags'),
        candidate_data.get('why_interesting'),
        json.dumps(candidate_data.get('therapeutic_areas', [])),
        json.dumps(candidate_data.get('phase_experience', [])),
        candidate_data.get('transcript'),
        json.dumps(candidate_data.get('search_tags', [])),
        candidate_data.get('attachment_path')
    ))

    candidate_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return candidate_id

def search_candidates(filters=None):
    """Search candidates with optional filters"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM candidates WHERE 1=1"
    params = []

    if filters:
        if filters.get('therapeutic_area'):
            query += " AND therapeutic_areas LIKE ?"
            params.append(f"%{filters['therapeutic_area']}%")

        if filters.get('phase'):
            query += " AND phase_experience LIKE ?"
            params.append(f"%{filters['phase']}%")

        if filters.get('company'):
            query += " AND current_company LIKE ?"
            params.append(f"%{filters['company']}%")

        if filters.get('search_tag'):
            query += " AND search_tags LIKE ?"
            params.append(f"%{filters['search_tag']}%")

        if filters.get('days_back'):
            query += " AND created_at >= datetime('now', '-' || ? || ' days')"
            params.append(filters['days_back'])

    query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    candidates = []
    for row in rows:
        candidate = dict(row)
        candidate['technical_skills'] = json.loads(candidate['technical_skills']) if candidate['technical_skills'] else []
        candidate['therapeutic_areas'] = json.loads(candidate['therapeutic_areas']) if candidate['therapeutic_areas'] else []
        candidate['phase_experience'] = json.loads(candidate['phase_experience']) if candidate['phase_experience'] else []
        candidate['search_tags'] = json.loads(candidate['search_tags']) if candidate['search_tags'] else []
        candidates.append(candidate)

    conn.close()
    return candidates

def get_candidate(candidate_id):
    """Get a single candidate by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    row = cursor.fetchone()

    if row:
        candidate = dict(row)
        candidate['technical_skills'] = json.loads(candidate['technical_skills']) if candidate['technical_skills'] else []
        candidate['therapeutic_areas'] = json.loads(candidate['therapeutic_areas']) if candidate['therapeutic_areas'] else []
        candidate['phase_experience'] = json.loads(candidate['phase_experience']) if candidate['phase_experience'] else []
        candidate['search_tags'] = json.loads(candidate['search_tags']) if candidate['search_tags'] else []
    else:
        candidate = None

    conn.close()
    return candidate
