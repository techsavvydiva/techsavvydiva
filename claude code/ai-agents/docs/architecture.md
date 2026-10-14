# Architecture And Current Repository State

This document distinguishes what exists in the repository from decisions and workflows that are planned but not built. The state summary reflects the repository inspected on 2026-10-14.

## Current Repository Layout

- `app/` — shared runtime package. `main.py` defines parsing for `--agent` and `--task` and a call to the current environment loader inside `main()`, but does not invoke `main()` when run as a script; `config.py` selects a per-agent `.env` file; `llm.py` provides a direct Anthropic client factory. `graph.py`, `models.py`, `storage.py`, and files under `app/tools/` are placeholders/empty.
- `agents/snobos/` — Snobos package with `agent.py`, `prompts.py`, `tools.py`, and a non-empty `config.yaml`. The YAML currently has agent metadata, a model name, tool allowlists, approval-required tool names, and an output directory; it is not loaded by the shared runtime.
- `agents/techsavvydiva/` — personal-agent package with the same scaffolded module names; no functioning workflow is implemented.
- `agents/synthesized_future/` — business/consulting-agent package with the same scaffolded module names; no functioning workflow is implemented.
- `agents/configs/` — agent configuration area exists but has no implemented loader path described by the runtime.
- `configs/` — per-agent environment files are present. This document does not reproduce or inspect their secret contents.
- `data/` — per-agent output directories are scaffolded. The repository ignore rules ignore `data/`, including Snobos rundowns.
- `docs/plans/` — versioned plans for Snobos v1, v2, and v3. `docs/templates/` exists, but no show-notes template is present yet.
- `notebooks/prompt_experiments.ipynb` — present, currently empty with no cells.
- `tests/test_tools.py` — present, currently empty.
- Root files include `README.md`, `pyproject.toml`, `uv.lock`, and `.python-version`.

## Configuration And Secrets

### Agreed target

- Each agent's YAML is authoritative for its model selection and non-secret settings.
- Each agent's environment file holds secrets only. Snobos specifically loads `configs/snobos.env` for `ANTHROPIC_API_KEY`; the root `.env` and other agents' env files must not be fallback sources. An explicit experiment override may be supported.
- Credentials and OAuth tokens for later integrations belong in `secrets/`, never in YAML, logs, or Git. Before creating that directory or storing files there, add and verify `secrets/` in `.gitignore`.

### Current implementation

- The shared `app/config.py` maps agent names to `configs/<agent>.env` and loads dotenv values. It does not parse per-agent YAML, so the agreed YAML authority/secrets-only separation is not implemented yet.
- `app/llm.py` reads `ANTHROPIC_API_KEY` from process environment and constructs an Anthropic SDK client.
- Snobos YAML exists, but the TechSavvyDiva and Synthesized Future YAML files are placeholders. YAML settings are not currently applied to the model client.
- `.gitignore` ignores `.env`, `configs/*.env`, `data/`, and `data/snobos/rundowns/`; it does not currently ignore `secrets/`.

## Planned Snobos Workflow

The following pipeline is the intended design, not current runtime behavior:

```text
show date + episode selection
        |
        v
show window (configurable; default 7 days, America/New_York)
        |
        +--> RSS: 9to5Mac, AppleInsider, MacRumors
        +--> Claude built-in web search (provider interface; cap default 10)
        |
        v
normalized story records
        |
        v
source/date/content verification (planned; exact verification policy to be specified)
        |
        v
deduplicate while preserving all useful source links
        |
        v
group into exact show segments
        |
        v
Stage 1 local rundown: data/snobos/rundowns/<episode> Rundown.md
        |
        +--> (planned Stage 2) slate: <episode> Slate.md
        |
        +--> (planned Stage 3) template-based show notes: <episode> Show Notes.md
        |
        +--> (planned V2/V3) approved Docs, livestream, Patreon,
             podcast-host, YouTube, and social integrations
```

### Stage distinctions

- **Stage 1 (planned v1):** Gather a comprehensive, unranked pool of story candidates from RSS and web search; normalize, verify, deduplicate, group, and write a Markdown rundown. Segment allocations describe a later show slate, not a limit on Stage 1 candidates.
- **Stage 2 (planned):** Prepare the episode slate and show logistics. V2 includes Google Docs output, scheduling the weekly livestream to YouTube, Patreon supporter notification, and automatic draft-rundown runs ahead of the user's show weeks.
- **Stage 3 (planned):** Create show notes using the existing show-notes template. A copy of the template must be added to the repo before implementation. V2 describes Google Docs output using this template.
- **V3 (planned):** Episode distribution and video teasers to the platforms documented in `docs/plans/snobos-v3.md`. Every publishing/notification action requires explicit approval. Nothing auto-posts.
- **snobist Show:** A 15-minute Patreon-exclusive show is a future consideration only. It has not been designed or built; questions remain about independent sourcing/notes, reporting-window sharing, and content distinction.

## Episode Numbering And Producer Rotation

- Anchor: Wednesday, October 14, 2026 is episode 383. Store this date and episode number in Snobos YAML.
- The main show normally occurs every Wednesday. Each show that occurs increments the episode by one regardless of producer.
- A configured skipped show date (holiday/off week) consumes no episode number. A CLI episode-number override is planned for exceptional corrections.
- The user's producer rotation is every other show, anchored at episode 383 on October 14, 2026; the next user-produced show is episode 385 on October 28, 2026.
- V2 scheduled rundown generation is planned ahead of user-produced weeks, on a two-week cadence anchored to that user rotation. Exact lead time, skip handling, and scheduler host remain open decisions.
- All dates/windows are interpreted in `America/New_York`; the default research window is seven local calendar days ending on the show date, inclusive of that date.

## Outputs And Git

- Planned Stage 1 output: `data/snobos/rundowns/<episode> Rundown.md`, e.g. `data/snobos/rundowns/383 Rundown.md`.
- Planned Stage 2 output: `<episode> Slate.md`.
- Planned Stage 3 output: `<episode> Show Notes.md`.
- Every generated file begins with episode number and show date.
- `data/` is ignored by Git, so generated rundowns and future local outputs are not committed.
- Secret environment files are ignored by current rules. The planned `secrets/` integration credentials/token directory is not yet ignored; this must be corrected before credentials are stored.
- Plans and architecture documentation belong in Git. Do not commit API keys, OAuth client files/tokens, stream keys, or generated outputs.

## Guardrails

- **Search budget (planned):** YAML-configurable maximum number of Claude web searches per run; default approximately 10, enforced by runtime. RSS fetches do not count toward the search cap.
- **Usage visibility (planned):** Log search count and available input/output token usage at run end. Never log secrets.
- **Candidate handling (planned):** Keep relevant candidates comprehensive and unranked; deduplicate overlap without dropping useful sources. Do not claim exhaustive Internet coverage. Surface source failures rather than silently calling a partial run complete.
- **Output permissions (planned):** V1 writes local Markdown only. It does not publish externally.
- **Human approval (planned for V2/V3):** Require explicit approval immediately before every external publish, upload, schedule, or supporter notification. Do not auto-post to public channels. Draft generation and external write permissions should remain separate.
- **Credential handling (planned):** Snobos API key is loaded specifically from `configs/snobos.env`; integration OAuth credentials/tokens are stored locally under a gitignored `secrets/` directory and never printed or committed.

## Shared Platform And Other Agents

The intended architecture keeps common CLI/configuration, Anthropic client construction, data contracts, output storage, and reusable read-only tools under `app/`. Brand-specific prompts, tools, settings, and workflows belong in their respective `agents/<name>/` packages. This boundary is planned; at present the shared workflow, storage, and tool implementations are empty, and the three agents do not execute tasks.

The project metadata declares Python `>=3.12` and LangChain/LangGraph dependencies. V1's approved direction is a direct Anthropic client and framework-agnostic tools/prompts; LangGraph is deferred. `uv.lock` was found inconsistent with the Python minimum and should be refreshed when dependency setup work is approved.
