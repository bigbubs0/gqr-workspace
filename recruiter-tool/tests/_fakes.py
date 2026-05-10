"""Reusable fake OpenAI client + fixture payloads for the recruiter-tool tests.

Kept out of conftest.py so that test modules can import these names directly
without depending on pytest's conftest import semantics.
"""

from __future__ import annotations

import json


VALID_CANDIDATE_PAYLOAD = {
    "name": "Jane Doe",
    "current_company": "Acme Bio",
    "current_title": "Director",
    "years_experience_total": 12,
    "years_experience_therapeutic": 8,
    "technical_skills": ["Phase 2"],
    "compensation_current_min": 200,
    "compensation_current_max": 220,
    "compensation_target_min": 240,
    "compensation_target_max": 260,
    "notice_period": "2 weeks",
    "location": "Boston, MA",
    "open_to_relocation": False,
    "red_flags": "",
    "why_interesting": "Strong fit.",
    "therapeutic_areas": ["oncology"],
    "phase_experience": ["Phase 2", "Phase 3"],
}


class FakeUsage:
    def __init__(self, input_tokens: int, output_tokens: int, cached_tokens: int):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = input_tokens + output_tokens
        self.input_tokens_details = {"cached_tokens": cached_tokens}


class FakeResponse:
    def __init__(
        self,
        payload: dict,
        *,
        response_id: str = "resp_test",
        input_tokens: int = 1500,
        output_tokens: int = 320,
        cached_tokens: int = 450,
    ):
        self.id = response_id
        self.output_text = json.dumps(payload)
        self.usage = FakeUsage(input_tokens, output_tokens, cached_tokens)


class FakeResponsesAPI:
    def __init__(self, actions):
        self._actions = list(actions)

    def create(self, **kwargs):
        action = self._actions.pop(0)
        if isinstance(action, Exception):
            raise action
        return action


class FakeClient:
    def __init__(self, actions):
        self.responses = FakeResponsesAPI(actions)


class TemporaryConnectionError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code
