# Snobos Build Log

## Step 1: CLI, Config Loading, And Show-Window Calculation

### What Was Built

- Added validated loading of Snobos YAML settings and a separate reader for `ANTHROPIC_API_KEY` from `configs/snobos.env`.
- Added a direct Anthropic client factory that requires an explicit key; constructing the client does not call the API.
- Added a CLI requiring `--show-date`, with optional `--episode-number`; it reports the resolved episode and window but does not fetch sources yet.
- Added pure helpers for the inclusive reporting window, weekly episode numbering, skipped Wednesdays, and user producer rotation.
- Added focused tests and Ruff configuration for Google-style docstrings.

### Key Decisions And Why

- Used `yaml.safe_load` and explicit validation instead of reading YAML with custom string parsing. YAML is the agreed settings source and should fail clearly when malformed.
- Kept secrets out of the settings dataclass and used `dotenv_values` on the explicit Snobos env path. It returns the requested value without mutating global environment state or consulting the root `.env`.
- Kept calendar logic in `app/schedule.py` as pure functions. It needs no model, SDK call, network, or filesystem and is easy to test at boundaries.
- Episode numbers count every Wednesday from the anchor, minus configured skipped Wednesdays. The episode override changes a run's display number but does not change the stored schedule.
- Set the user's rotation to begin at episode 385, every two occurring episodes; episode 383 is the episode-number anchor, not the first user-produced episode.
- The window starts on the previous occurring show Wednesday and ends on the current show Wednesday, inclusive. A normal weekly interval is seven elapsed days and therefore covers eight calendar dates; a skipped show week extends the window to the prior occurring show.
- Kept the CLI at a setup checkpoint: validate config/secret/client and print dates; source adapters arrive in later steps.

### Concepts Introduced

- **Configuration boundary:** versioned non-secret settings (YAML) are separate from credentials (env file).
- **Deterministic scheduling:** exact calendar and rotation rules are regular code, not model judgment.
- **Explicit dependency passing:** client creation receives the selected agent key instead of reading ambient process state.
- **Testable CLI:** `main(argv)` accepts arguments directly, so tests can run it without a subprocess or live service.
- **Reusable pattern:** config validation, explicit secret loading, Anthropic client setup, and date helpers belong in shared `app/`; later agents can reuse those pieces while defining their own settings schema.

### Surprises Or Mistakes

- The first implementation treated `window_days=7` as seven included dates and started Oct 8 for episode 383. The intended interval is Oct 7–14 inclusive; tests now assert this and the Nov 11–18 window.
- This checkpoint does not yet produce a rundown. A successful CLI run only confirms configuration and schedule readiness; RSS, web search, and output are later steps.
- The first repo-wide Ruff run found missing module docstrings throughout empty scaffold packages plus an invalid empty notebook file. Added role-only module docstrings without implementing the other agents, and excluded notebooks from Python lint because the placeholder is not valid notebook JSON or Python source.
- Direct `python app/main.py` does not put the repository root on the import path in this project. The supported manual command is `python -m app.main`; no import-path mutation was added to the application.

### What To Inspect

- `app/config.py`: settings schema, YAML validation, and env-file isolation.
- `app/schedule.py`: show-window, skipped-week, episode, and producer-rotation arithmetic.
- `app/main.py`: CLI argument flow and the point where later collection will attach.
- `app/llm.py`: explicit key handoff to the Anthropic SDK.
- `agents/snobos/config.yaml`: the anchor, timezone, window, search cap, skips, and producer rotation values.
- `tests/test_snobos_stage1.py`: known-answer dates and invalid-input behavior.

### Checkpoint Validation

Run the Step 1 tests and lint with:

```bash
uv run python -m pytest -q tests/test_snobos_stage1.py
uv run ruff check
```

Manual check:

```bash
uv run python -m app.main --show-date 2026-10-14
uv run python -m app.main --show-date 2026-10-28
uv run python -m app.main --show-date 2026-10-28 --episode-number 999
```

Validation completed before the window correction: `uv run python -m pytest -q tests/test_snobos_stage1.py` passed (12 tests), and `uv run ruff check` passed repository-wide. `uv lock --check` and `git diff --check` also passed. Manual module-form CLI checks passed for episode calculation and overrides, but the reported window boundary was subsequently corrected in this checkpoint. Running `python app/main.py` directly does not resolve the `app` package from this uninstalled repository, so module invocation (`python -m app.main`) is the supported Step 1 command.

### Window Correction Checkpoint

- Corrected `get_show_window` to start at the previous occurring Wednesday and end on the show Wednesday, inclusive. If the immediately previous scheduled Wednesday is skipped, it walks back to the last Wednesday when a show occurred.
- Updated exact tests for Oct 7–14 and Nov 11–18, plus a skipped-week boundary test.
- Validation after the correction: `uv run python -m pytest -q tests/test_snobos_stage1.py` passed (14 tests), and `uv run ruff check` passed repository-wide.
- Manual checks passed for `uv run python -m app.main --show-date 2026-11-18 --episode-number 388` and `uv run python -m app.main --show-date 2026-10-14 --episode-number 383`; both printed the expected inclusive Wednesday-to-Wednesday windows and stated that no sources were queried.