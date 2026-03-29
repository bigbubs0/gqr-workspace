"""Tests for recruiter-tool/app.py Flask API endpoints."""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import database


class TestIndexRoute:
    """Tests for GET /."""

    def test_index_returns_200(self, app_client):
        response = app_client.get('/')
        assert response.status_code == 200


class TestProcessTranscript:
    """Tests for POST /api/process."""

    def test_returns_400_when_no_transcript(self, app_client):
        response = app_client.post(
            '/api/process',
            json={'transcript': ''},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_successful_processing(self, app_client, mocker):
        mock_extract = mocker.patch('app.extract_candidate_info', return_value={
            'name': 'Jane Doe',
            'current_company': 'Pfizer',
            'current_title': 'Director',
            'technical_skills': ['Phase 3'],
            'therapeutic_areas': ['oncology'],
            'phase_experience': ['Phase 3'],
        })

        response = app_client.post(
            '/api/process',
            json={'transcript': 'Jane Doe from Pfizer', 'search_tags': ['oncology']},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'candidate_id' in data
        assert 'brief' in data
        assert 'data' in data
        mock_extract.assert_called_once()

    def test_returns_500_on_ai_error(self, app_client, mocker):
        mocker.patch('app.extract_candidate_info', side_effect=Exception('API down'))
        response = app_client.post(
            '/api/process',
            json={'transcript': 'Some text'},
        )
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data


class TestSearchRoute:
    """Tests for GET /api/search."""

    def test_returns_empty_results(self, app_client):
        response = app_client.get('/api/search')
        data = response.get_json()
        assert data['success'] is True
        assert data['count'] == 0
        assert data['candidates'] == []

    def test_returns_saved_candidates(self, app_client, sample_candidate, tmp_db):
        database.save_candidate(sample_candidate)
        response = app_client.get('/api/search')
        data = response.get_json()
        assert data['count'] == 1

    def test_filters_by_company(self, app_client, sample_candidate, tmp_db):
        database.save_candidate(sample_candidate)
        response = app_client.get('/api/search?company=Genentech')
        data = response.get_json()
        assert data['count'] == 1

        response = app_client.get('/api/search?company=Pfizer')
        data = response.get_json()
        assert data['count'] == 0


class TestGetCandidateDetail:
    """Tests for GET /api/candidate/<id>."""

    def test_returns_candidate(self, app_client, sample_candidate, tmp_db):
        cid = database.save_candidate(sample_candidate)
        response = app_client.get(f'/api/candidate/{cid}')
        data = response.get_json()
        assert data['success'] is True
        assert data['candidate']['name'] == 'Jane Smith'
        assert 'brief' in data

    def test_returns_404_for_nonexistent(self, app_client):
        response = app_client.get('/api/candidate/9999')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data


class TestExportCandidates:
    """Tests for POST /api/export."""

    def test_exports_formatted_text(self, app_client, sample_candidate, tmp_db):
        database.save_candidate(sample_candidate)
        response = app_client.post('/api/export', json={'filters': {}})
        data = response.get_json()
        assert data['success'] is True
        assert data['count'] == 1
        assert 'CANDIDATE #1' in data['export_text']
        assert 'Jane Smith' in data['export_text']

    def test_exports_empty_when_no_matches(self, app_client):
        response = app_client.post('/api/export', json={'filters': {'company': 'None'}})
        data = response.get_json()
        assert data['count'] == 0


class TestUploadAttachment:
    """Tests for POST /api/candidate/<id>/upload."""

    def test_returns_400_when_no_file(self, app_client, sample_candidate, tmp_db):
        cid = database.save_candidate(sample_candidate)
        response = app_client.post(f'/api/candidate/{cid}/upload')
        assert response.status_code == 400

    def test_returns_400_for_disallowed_type(self, app_client, sample_candidate, tmp_db, mocker):
        cid = database.save_candidate(sample_candidate)
        mocker.patch('app.save_attachment', side_effect=ValueError('File type not allowed'))
        from io import BytesIO
        data = {'file': (BytesIO(b'content'), 'malware.exe')}
        response = app_client.post(
            f'/api/candidate/{cid}/upload',
            data=data,
            content_type='multipart/form-data',
        )
        assert response.status_code == 400


class TestGetCandidateAttachments:
    """Tests for GET /api/candidate/<id>/attachments."""

    def test_returns_empty_list(self, app_client, sample_candidate, tmp_db):
        cid = database.save_candidate(sample_candidate)
        response = app_client.get(f'/api/candidate/{cid}/attachments')
        data = response.get_json()
        assert data['success'] is True
        assert data['attachments'] == []


class TestDeleteAttachmentRoute:
    """Tests for DELETE /api/attachment/<id>."""

    def test_returns_success(self, app_client, tmp_db):
        response = app_client.delete('/api/attachment/9999')
        data = response.get_json()
        assert data['success'] is True
