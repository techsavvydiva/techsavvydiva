# Snobos V1 Plan

## Goal

Build the first working Snobos workflow: a weekly, comprehensive rundown of discovered story candidates for the podcast. The rundown is a research input, not a curated list of picks. Show notes, episode titles, hashtags, transcript support, and external publishing are out of scope for v1.

## Reporting Window

- The window is configurable in the Snobos YAML configuration, with a default of seven days.
- Each run takes a recording day as its end date. Include that recording day and the six preceding local calendar days.
- Interpret dates in `America/New_York`; use this timezone for the reporting window and date displayed in the rundown.
- Keep the window logic independent of the machine's local timezone.

## Sources And Search

- Use Claude's built-in web search tool through the Anthropic API for web discovery.
- Read RSS feeds from 9to5Mac, AppleInsider, and MacRumors.
- Do not use podcast transcripts in v1.
- Put search behind a small provider interface so a dedicated provider such as Tavily or Exa can be substituted later without changing agent prompts or workflow logic.
- Preserve source links when results overlap; deduplicate stories without discarding distinct useful sources.
- Include all discovered candidates relevant to the show segments. Apply topical/date relevance and duplicate handling, but do not rank candidates or editorially reduce them to a shortlist. Do not claim exhaustive coverage of the internet.

## Rundown Format

Write Markdown grouped under these segments, in this order:

1. The Lowdown (Apple stories)
2. 2nd String (non-Apple tech)
3. For the Culture (Black culture and pop culture)
4. The Hookup (consumer safety and tips)

Each candidate includes a headline, a one- or two-sentence summary, source link(s), and date. Use the story's publication date when available; make missing dates explicit rather than inventing one. A story should appear in the most relevant segment, without being omitted merely because it is not a top pick.

Save each run to `data/snobos/rundowns/YYYY-MM-DD.md`, using the recording day for the filename. The rundowns directory is generated output and must remain ignored by Git.

## Cost And Secret Guardrails

- Configure a maximum number of Claude web searches per run in the Snobos YAML; default to 10.
- Enforce the cap in the runtime, not only in the prompt. RSS requests do not count as web searches.
- At the end of each run, log the web search count and available input/output token usage. Do not log API keys or other secrets.
- Load the Anthropic API key specifically from `configs/snobos.env`. Do not use the root `.env` or another agent's env file for Snobos. An optional explicit environment override may be supported for experiments.
- Keep external write actions out of v1; collection and local Markdown output are read-only with respect to external services.

## Implementation Steps And Checkpoints

Stop after setup and after each numbered step for user review. Do not start a subsequent step until the user says to continue. Update this plan whenever an approved implementation decision changes.

### Setup (this checkpoint)

- Save this plan under `docs/plans/` and ensure documentation can be committed.
- Keep the existing root `README.md`; do not move it or add `docs/README.md`.
- Explicitly ignore `data/snobos/rundowns/`.

### Step 1: Runtime And Configuration

- Make the CLI execute a Snobos run and accept the recording day.
- Load the Snobos YAML settings and `configs/snobos.env` secret.
- Keep the direct Anthropic client for v1; do not add LangGraph.
- Define typed, framework-agnostic settings and story data structures.

### Step 2: Search And RSS Sources

- Implement the replaceable web search provider using Claude's built-in API tool, enforcing the configured search cap.
- Implement RSS readers for the three named publications.
- Normalize results to the shared story structure and show the user sample normalized records from each source at this checkpoint.

### Step 3: Weekly Candidate Collection

- Collect candidates for the configured seven-day window ending on the supplied recording day.
- Normalize dates to the configured timezone, deduplicate overlaps while retaining sources, and assign candidates to the four show segments.
- Keep candidate collection comprehensive and unranked; report source-level failures without silently presenting a partial run as complete.

### Step 4: Rundown Generation And Output

- Generate the grouped Markdown rundown with headlines, short summaries, links, and dates.
- Write it to `data/snobos/rundowns/YYYY-MM-DD.md` and log search count and token usage.

### Step 5: Tests And End-To-End Check

- Add focused tests for config/secrets selection, the reporting window, search limits, RSS parsing, normalization, deduplication, segment grouping, output format/path, and usage/search logging.
- Run the test suite and perform a live smoke test with the user's configured Anthropic key, without exposing the key in output or logs.

## V1 Completion Criteria

- Running the CLI for a recording day uses the Snobos YAML settings and only the Snobos secret file by default.
- The collection window is seven local calendar days, inclusive of the recording day, in `America/New_York`, unless changed in YAML.
- Claude web searches never exceed the configured cap; the default is 10.
- RSS and web candidates are combined, deduplicated with source links retained, and grouped into the four segments without ranking or shortlisting.
- A dated Markdown rundown is written to the required ignored output directory, with search count and token usage logged at run end.