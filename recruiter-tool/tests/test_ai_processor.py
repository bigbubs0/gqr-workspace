"""Tests for recruiter-tool/ai_processor.py"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from ai_processor import generate_candidate_brief, extract_candidate_info


class TestGenerateCandidateBrief:
    """Tests for generate_candidate_brief() - pure function, no mocking needed."""

    def test_header_format(self, sample_candidate):
        brief = generate_candidate_brief(sample_candidate)
        assert brief.startswith('Jane Smith - VP Clinical Development at Genentech')

    def test_includes_key_qualifications_section(self, sample_candidate):
        brief = generate_candidate_brief(sample_candidate)
        assert 'KEY QUALIFICATIONS:' in brief

    def test_includes_technical_skills(self, sample_candidate):
        brief = generate_candidate_brief(sample_candidate)
        assert '- IND filings' in brief
        assert '- Phase 3 trials' in brief
        assert '- Oncology' in brief

    def test_limits_skills_to_eight(self):
        data = {
            'name': 'Test',
            'current_title': 'Title',
            'current_company': 'Company',
            'technical_skills': [f'Skill {i}' for i in range(12)],
        }
        brief = generate_candidate_brief(data)
        # Should include first 8 skills
        assert '- Skill 7' in brief
        assert '- Skill 8' not in brief

    def test_includes_experience_years(self, sample_candidate):
        brief = generate_candidate_brief(sample_candidate)
        assert '18 years total experience' in brief
        assert '12 years in relevant therapeutic area' in brief

    def test_includes_therapeutic_areas(self, sample_candidate):
        brief = generate_candidate_brief(sample_candidate)
        assert 'oncology, rare disease' in brief

    def test_includes_phase_experience(self, sample_candidate):
        brief = generate_candidate_brief(sample_candidate)
        assert 'Phase 2, Phase 3, NDA/BLA' in brief

    def test_includes_compensation_section(self, sample_candidate):
        brief = generate_candidate_brief(sample_candidate)
        assert 'COMPENSATION & AVAILABILITY:' in brief
        assert 'Current: $280-$320K' in brief
        assert 'Target: $350-$400K' in brief

    def test_compensation_with_min_only(self):
        data = {
            'name': 'Test',
            'current_title': 'Title',
            'current_company': 'Company',
            'compensation_current_min': 200,
            'compensation_current_max': None,
            'compensation_target_min': 250,
            'compensation_target_max': None,
        }
        brief = generate_candidate_brief(data)
        assert 'Current: $200K' in brief
        assert 'Target: $250K' in brief

    def test_compensation_not_disclosed(self):
        data = {
            'name': 'Test',
            'current_title': 'Title',
            'current_company': 'Company',
        }
        brief = generate_candidate_brief(data)
        assert 'Current: Not disclosed' in brief
        assert 'Target: Not disclosed' in brief

    def test_includes_availability(self, sample_candidate):
        brief = generate_candidate_brief(sample_candidate)
        assert 'Available: 2 weeks' in brief

    def test_includes_location_and_relocation(self, sample_candidate):
        brief = generate_candidate_brief(sample_candidate)
        assert 'Location: South San Francisco, CA' in brief
        assert 'Open to relocation: Y' in brief

    def test_relocation_no(self):
        data = {
            'name': 'Test',
            'current_title': 'Title',
            'current_company': 'Company',
            'open_to_relocation': False,
        }
        brief = generate_candidate_brief(data)
        assert 'Open to relocation: N' in brief

    def test_includes_why_interesting(self, sample_candidate):
        brief = generate_candidate_brief(sample_candidate)
        assert 'WHY THIS CANDIDATE IS INTERESTING:' in brief
        assert 'Strong Genentech pedigree' in brief

    def test_includes_red_flags_when_present(self):
        data = {
            'name': 'Test',
            'current_title': 'Title',
            'current_company': 'Company',
            'red_flags': 'Short tenure at last two companies',
        }
        brief = generate_candidate_brief(data)
        assert 'RED FLAGS / CONCERNS:' in brief
        assert 'Short tenure at last two companies' in brief

    def test_red_flags_none_identified(self, sample_candidate):
        brief = generate_candidate_brief(sample_candidate)
        assert 'None identified' in brief

    def test_handles_missing_fields_gracefully(self):
        data = {'name': 'Minimal Candidate'}
        brief = generate_candidate_brief(data)
        assert 'Minimal Candidate' in brief
        assert 'Unknown Title' in brief
        assert 'Unknown Company' in brief

    def test_empty_skills_list(self):
        data = {
            'name': 'Test',
            'current_title': 'Title',
            'current_company': 'Company',
            'technical_skills': [],
        }
        brief = generate_candidate_brief(data)
        assert 'KEY QUALIFICATIONS:' in brief


class TestExtractCandidateInfo:
    """Tests for extract_candidate_info() - requires mocking OpenAI client."""

    def test_successful_extraction(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.choices = [mocker.MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            'name': 'Jane Doe',
            'current_company': 'Pfizer',
            'current_title': 'Director Clinical Development',
            'years_experience_total': 15,
            'technical_skills': ['Phase 3', 'Oncology'],
            'therapeutic_areas': ['oncology'],
            'phase_experience': ['Phase 2', 'Phase 3'],
        })

        mock_client = mocker.MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mocker.patch('ai_processor.get_client', return_value=mock_client)

        result = extract_candidate_info('Jane Doe works at Pfizer as Director.')
        assert result['name'] == 'Jane Doe'
        assert result['current_company'] == 'Pfizer'
        assert 'Oncology' in result['technical_skills']

    def test_api_error_raises_exception(self, mocker):
        mock_client = mocker.MagicMock()
        mock_client.chat.completions.create.side_effect = Exception('API rate limit')
        mocker.patch('ai_processor.get_client', return_value=mock_client)

        with pytest.raises(Exception, match='AI extraction failed'):
            extract_candidate_info('Some transcript')

    def test_sends_transcript_in_prompt(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.choices = [mocker.MagicMock()]
        mock_response.choices[0].message.content = json.dumps({'name': 'Test'})

        mock_client = mocker.MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mocker.patch('ai_processor.get_client', return_value=mock_client)

        extract_candidate_info('My unique transcript text')

        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]['messages'][1]['content']
        assert 'My unique transcript text' in user_message

    def test_uses_json_response_format(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.choices = [mocker.MagicMock()]
        mock_response.choices[0].message.content = json.dumps({'name': 'Test'})

        mock_client = mocker.MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mocker.patch('ai_processor.get_client', return_value=mock_client)

        extract_candidate_info('transcript')

        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['response_format'] == {'type': 'json_object'}
