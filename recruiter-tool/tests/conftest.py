"""Shared pytest fixtures for the recruiter-tool test suite.

The recruiter-tool modules read configuration (DB_PATH, telemetry dir, OpenAI
env vars) at import time, so each test gets a freshly loaded module stack
pointed at a temporary directory.
"""

from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Iterator

import pytest

from _fakes import FakeClient, TemporaryConnectionError  # noqa: F401 — re-exported


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


_APP_MODULE_NAMES = ("app", "ai_processor", "costing", "database", "file_handler", "telemetry")


def _purge_modules() -> None:
    for name in _APP_MODULE_NAMES:
        sys.modules.pop(name, None)


def _load_stack(temp_dir: Path) -> SimpleNamespace:
    _purge_modules()
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

    return SimpleNamespace(
        app=app_module,
        ai_processor=ai_processor,
        database=database,
        file_handler=file_handler,
        telemetry=telemetry,
        costing=costing,
        temp_dir=temp_dir,
    )


@pytest.fixture
def app_stack(tmp_path: Path) -> Iterator[SimpleNamespace]:
    stack = _load_stack(tmp_path)
    yield stack
    _purge_modules()


@pytest.fixture
def client(app_stack: SimpleNamespace):
    return app_stack.app.app.test_client()


@pytest.fixture
def telemetry_lines(app_stack: SimpleNamespace):
    def _read(filename: str) -> list[dict]:
        path = app_stack.temp_dir / "telemetry" / filename
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    return _read


@pytest.fixture
def fake_client_factory(app_stack: SimpleNamespace):
    """Returns a callable that, given a list of actions (responses or exceptions),
    installs a fake OpenAI client on ai_processor.get_client."""

    original_error_class = app_stack.ai_processor.APIConnectionError
    app_stack.ai_processor.APIConnectionError = TemporaryConnectionError

    def _make(actions):
        client = FakeClient(actions)
        app_stack.ai_processor.get_client = lambda: client
        return client

    yield _make

    app_stack.ai_processor.APIConnectionError = original_error_class
