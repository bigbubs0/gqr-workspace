from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def purge_modules() -> None:
    for module_name in ["app", "ai_processor", "costing", "database", "file_handler", "telemetry"]:
        sys.modules.pop(module_name, None)


def load_app_stack(temp_dir: Path):
    purge_modules()
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["OPENAI_MODEL"] = "gpt-5.4"
    os.environ["OPENAI_REASONING_EFFORT"] = "medium"
    os.environ["TELEMETRY_ENABLED"] = "true"
    os.environ["TELEMETRY_DIR"] = str(temp_dir / "telemetry")
    os.environ["TELEMETRY_LOG_RAW_PROMPTS"] = "false"

    database = importlib.import_module("database")
    database.DB_PATH = str(temp_dir / "candidates.db")

    file_handler = importlib.import_module("file_handler")
    file_handler.DB_PATH = database.DB_PATH
    file_handler.UPLOAD_FOLDER = str(temp_dir / "uploads")

    app_module = importlib.import_module("app")
    app_module.DB_PATH = database.DB_PATH
    app_module.app.config["TESTING"] = True

    ai_processor = importlib.import_module("ai_processor")
    telemetry = importlib.import_module("telemetry")
    costing = importlib.import_module("costing")
    return app_module, ai_processor, database, telemetry, costing


class FakeUsage:
    def __init__(self, input_tokens: int, output_tokens: int, cached_tokens: int):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = input_tokens + output_tokens
        self.input_tokens_details = {"cached_tokens": cached_tokens}


class FakeResponse:
    def __init__(self, payload: dict, *, response_id: str = "resp_test", input_tokens: int = 1500, output_tokens: int = 320, cached_tokens: int = 450):
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


class TelemetryV1Tests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="recruiter-tool-tests-"))
        self.app_module, self.ai_processor, self.database, self.telemetry, self.costing = load_app_stack(self.temp_dir)
        self.client = self.app_module.app.test_client()

    def tearDown(self):
        purge_modules()

    def _telemetry_lines(self, filename: str) -> list[dict]:
        path = self.temp_dir / "telemetry" / filename
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_cost_formula_matches_expected_values(self):
        result = self.costing.estimate_gpt54_costs(input_tokens=1000, cached_input_tokens=250, output_tokens=200)
        self.assertAlmostEqual(result["llm.cost_input_usd"], 0.001875, places=8)
        self.assertAlmostEqual(result["llm.cost_cached_input_usd"], 0.0000625, places=8)
        self.assertAlmostEqual(result["llm.cost_output_usd"], 0.003, places=8)
        self.assertAlmostEqual(result["run.estimated_cost_usd"], 0.0049375, places=8)

    def test_call_candidate_extraction_retries_and_records_cached_tokens(self):
        original_error_class = self.ai_processor.APIConnectionError
        self.ai_processor.APIConnectionError = TemporaryConnectionError
        try:
            payload = {
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
            fake_client = FakeClient(
                [
                    TemporaryConnectionError("temporary network issue"),
                    FakeResponse(payload, cached_tokens=500),
                ]
            )

            candidate_data, metrics = self.ai_processor.call_candidate_extraction(
                fake_client,
                "Jane Doe from Acme Bio led Phase 2 oncology programs.",
                pipeline_run_id="run_retry_case",
            )
        finally:
            self.ai_processor.APIConnectionError = original_error_class

        self.assertEqual(candidate_data["name"], "Jane Doe")
        self.assertEqual(metrics["llm.retry_count"], 1)
        self.assertEqual(metrics["llm.cached_input_tokens"], 500)
        error_lines = self._telemetry_lines("errors.ndjson")
        self.assertTrue(any(line["name"] == "llm.candidate_extraction.retry" for line in error_lines))

    def test_process_route_success_writes_spans_summary_and_header_without_raw_transcript(self):
        payload = {
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
        self.ai_processor.get_client = lambda: FakeClient([FakeResponse(payload)])

        transcript = "Jane Doe currently works at Acme Bio and leads Phase 2 oncology studies."
        response = self.client.post("/api/process", json={"transcript": transcript, "search_tags": ["Aditum VP"]})

        self.assertEqual(response.status_code, 200)
        self.assertIn("X-Pipeline-Run-Id", response.headers)

        spans = self._telemetry_lines("custom-spans.ndjson")
        span_names = {span["name"] for span in spans}
        self.assertIn("http.process_candidate", span_names)
        self.assertIn("stage.llm_extract", span_names)
        self.assertIn("stage.db_save", span_names)

        summaries = self._telemetry_lines("run-summaries.ndjson")
        self.assertTrue(any(summary["route"] == "/api/process" for summary in summaries))

        telemetry_blob = (self.temp_dir / "telemetry" / "custom-spans.ndjson").read_text(encoding="utf-8")
        self.assertNotIn(transcript, telemetry_blob)

    def test_validation_failure_returns_500_logs_schema_failure_and_skips_db_insert(self):
        invalid_payload = {
            "name": "",
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
        self.ai_processor.get_client = lambda: FakeClient([FakeResponse(invalid_payload)])

        response = self.client.post(
            "/api/process",
            json={"transcript": "Acme Bio oncology background with unnamed candidate.", "search_tags": []},
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.database.search_candidates({}), [])

        summaries = self._telemetry_lines("run-summaries.ndjson")
        process_summary = summaries[-1]
        self.assertEqual(process_summary["quality.schema_failures"], 1)

    def test_final_llm_failure_returns_500_and_records_error_telemetry(self):
        original_error_class = self.ai_processor.APIConnectionError
        self.ai_processor.APIConnectionError = TemporaryConnectionError
        try:
            self.ai_processor.get_client = lambda: FakeClient(
                [
                    TemporaryConnectionError("first failure"),
                    TemporaryConnectionError("second failure"),
                    TemporaryConnectionError("third failure"),
                ]
            )

            response = self.client.post(
                "/api/process",
                json={"transcript": "Jane Doe from Acme Bio", "search_tags": []},
            )
        finally:
            self.ai_processor.APIConnectionError = original_error_class

        self.assertEqual(response.status_code, 500)
        error_lines = self._telemetry_lines("errors.ndjson")
        self.assertTrue(any(line["name"] == "llm.candidate_extraction" for line in error_lines))

    def test_search_route_writes_request_level_telemetry(self):
        response = self.client.get("/api/search?company=Acme")
        self.assertEqual(response.status_code, 200)
        self.assertIn("X-Pipeline-Run-Id", response.headers)
        summaries = self._telemetry_lines("run-summaries.ndjson")
        self.assertTrue(any(summary["route"] == "/api/search" for summary in summaries))

    def test_concurrent_span_writes_remain_valid_ndjson(self):
        def worker(index: int) -> None:
            with self.telemetry.span("test.concurrent", "test", f"run_{index}", worker=index):
                pass

        threads = [threading.Thread(target=worker, args=(index,)) for index in range(12)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        span_lines = self._telemetry_lines("custom-spans.ndjson")
        concurrent_lines = [line for line in span_lines if line["name"] == "test.concurrent"]
        self.assertEqual(len(concurrent_lines), 12)


if __name__ == "__main__":
    unittest.main()
