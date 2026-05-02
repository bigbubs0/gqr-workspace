# Dependency Scan & Upgrade Plan
**Date:** 2026-05-02
**Scanner:** `pip-audit` (PyPI advisory DB) + manual review
**Scope:** All declared dependencies in this repo

---

## 1. Inventory

Only one declared dependency manifest exists: `recruiter-tool/requirements.txt`.

```
flask==3.0.0
openai>=1.0.0
python-dotenv==1.0.0
```

The `autoresearch/` tool installs `anthropic` ad-hoc via `setup.sh` (`pip install anthropic`) and imports `matplotlib`, `numpy`, `pandas` in `analyze.py` without a manifest. No `package.json`, `Pipfile`, `pyproject.toml`, `poetry.lock`, `Cargo.toml`, `go.mod`, or `Gemfile` anywhere else. No GitHub Actions workflows (only `.github/agents/`).

**Gap:** `autoresearch/` has no pinned manifest. This is a supply-chain and reproducibility risk, but not the subject of this scan.

---

## 2. Findings

### Vulnerabilities (pip-audit)

| Package | Pinned | Fixed in | Advisory | Severity | Applies to us? |
|---|---|---|---|---|---|
| `flask` | 3.0.0 | 3.1.3 | [GHSA-68rp-wp8r-4726](https://github.com/advisories/GHSA-68rp-wp8r-4726) / CVE-2026-27205 — missing `Vary: Cookie` on some session access patterns behind a caching proxy | Low | **No.** `recruiter-tool/app.py` uses `g` (request context), not `session`. Not behind a shared caching proxy. Risk = theoretical. |
| `python-dotenv` | 1.0.0 | 1.2.2 | [GHSA-mf9w-mj56-hr94](https://github.com/advisories/GHSA-mf9w-mj56-hr94) / CVE-2026-28684 — `set_key()`/`unset_key()` follow symlinks, allowing cross-device symlink overwrite of arbitrary files | Low-Med | **No (current usage).** Code only calls `load_dotenv()` — read-only. Exploit requires `set_key`/`unset_key` on attacker-controlled paths. Still worth patching to avoid future footguns. |

### Outdated (no CVE, but drift)

| Package | Pinned | Latest | Drift |
|---|---|---|---|
| `flask` | 3.0.0 | 3.1.3 | 1 minor |
| `openai` | `>=1.0.0` (unpinned) | 2.33.0 | **1 major** (1.x → 2.x released) |
| `python-dotenv` | 1.0.0 | 1.2.2 | 2 minors |
| `werkzeug` (transitive) | pulled by Flask 3.0.x (2.3.x / 3.0.x) | 3.1.8 | in-range via Flask upgrade |

### Unpinned / undeclared

| Package | Where | Risk |
|---|---|---|
| `openai` | `requirements.txt` uses `>=1.0.0`, which floats into **2.x** — a major with breaking changes (see §4) | **High risk of silent breakage** on next `pip install` |
| `anthropic` | `autoresearch/setup.sh` bare `pip install anthropic` | Unpinned — undeclared reproducibility risk |
| `matplotlib`, `numpy`, `pandas` | `autoresearch/analyze.py` imports | Not declared anywhere |

### Deprecated

None detected. Flask 3.x, openai 1.x, python-dotenv 1.x are all actively maintained.

---

## 3. Likely Breaking Changes

### `openai` 1.x → 2.x (the one that matters)

`ai_processor.py` uses the **Responses API** (`client.responses.create(...)`) with `reasoning={"effort": ...}`, `text={"format": {"type": "json_schema", ...}}`, and catches `APIConnectionError`, `APIStatusError`, `APITimeoutError`, `RateLimitError`. Most of that surface is stable across the 1.x → 2.x bump, but the 2.x line has tightened typing around the Responses API, changed streaming event shapes, and adjusted some Pydantic model exports. Concretely, the codebase depends on:

- `client.responses.create(...)` signature — **stable**
- `response.output_text` / `output[].content[].type == "output_text"` — **stable**
- `usage.input_tokens_details.cached_tokens` — **stable**
- The four exception classes — **stable names**, same module
- `text={"format": {"type": "json_schema", "strict": True, "schema": ..., "name": ...}}` — this is the pre-2.x shape and still accepted, but 2.x prefers the newer `response_format=`/strict schema helpers. A forced upgrade is low-risk but should be smoke-tested.

**Verdict:** `openai` 1.x → 2.x should work with no code changes for this codebase, but `>=1.0.0` is a timebomb because `pip install` will pick 2.33.0 today and could pick 3.0 tomorrow. **Pin it.**

### `flask` 3.0 → 3.1

Flask 3.1 is a minor release. No breaking API removals touch this app. `make_response`, `send_file(... as_attachment=True, download_name=...)`, `jsonify`, and the `g` pattern all unchanged. Werkzeug is bumped to 3.1.x; `werkzeug.utils.secure_filename` (used in `file_handler.py`) is unchanged.

**Verdict:** zero-risk drop-in.

### `python-dotenv` 1.0 → 1.2.2

Minor bump. Only API used is `load_dotenv()` — unchanged. New `follow_symlinks` flag on `set_key`/`unset_key` is opt-in and we don't use those.

**Verdict:** zero-risk drop-in.

---

## 4. Smallest Safe Update Plan

Proposed diff to `recruiter-tool/requirements.txt`:

```diff
- flask==3.0.0
- openai>=1.0.0
- python-dotenv==1.0.0
+ flask==3.1.3
+ openai==2.33.0
+ python-dotenv==1.2.2
```

Rationale, in priority order:

1. **Pin `openai` to an exact version (highest-priority change).** `>=1.0.0` is the only real hazard in this file — it will silently pull whatever major is current at install time. Pinning to `2.33.0` locks the known-good surface that matches the Responses-API usage in `ai_processor.py`.
2. **Bump `python-dotenv` to `1.2.2`.** Clears CVE-2026-28684, trivially compatible.
3. **Bump `flask` to `3.1.3`.** Clears CVE-2026-27205, trivially compatible; `secure_filename`, `send_file`, `make_response`, `jsonify` all unchanged.

**Not in this plan (deliberately):**

- No changes to `autoresearch/` — it has no manifest; declaring deps there is a separate piece of work (create `autoresearch/requirements.txt` with pinned `anthropic`, `matplotlib`, `numpy`, `pandas`). Flagging as a follow-up.
- No `pyproject.toml` migration.
- No hashed requirements (nice-to-have, not needed for a 3-line file).

---

## 5. Validation Plan (before merging the bump)

Run locally after the edit:

```bash
cd recruiter-tool
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover tests   # test_telemetry_v1.py
pip-audit --disable-pip --no-deps -r requirements.txt
```

Expected:
- Unit tests pass (they stub the OpenAI client via `FakeUsage`, so they exercise the library's import surface without hitting the network).
- `pip-audit` returns 0 vulns.
- A manual smoke test of `/extract` in `app.py` against a real transcript confirms the 1.x→2.x upgrade doesn't regress the Responses API path.

---

## 6. Follow-ups (not part of this update)

- [ ] Add `autoresearch/requirements.txt` with pinned `anthropic`, `matplotlib`, `numpy`, `pandas`.
- [ ] Consider adding `pip-audit` to a pre-commit or CI step so drift is caught automatically.
- [ ] Remove `>=` ranges from any future manifest additions — always pin exact versions in this repo.
