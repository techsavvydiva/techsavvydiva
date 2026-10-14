# Snobos V1 Plan

## Goal

Build the first working Snobos workflow: a weekly, comprehensive rundown of discovered story candidates for the podcast. The rundown is a research input, not a curated list of picks. Show notes, episode titles, hashtags, transcript support, and external publishing are out of scope for v1.

## Reporting Window

- The window is configurable in the Snobos YAML configuration, with a default of seven days.
- Each run takes a recording/show day as its end date. Include that day and the six preceding local calendar days.
- Interpret dates in `America/New_York`; use this timezone for the reporting window and date displayed in the rundown.
- Keep the window logic independent of the machine's local timezone.

## Episode Numbering

- Store the episode-number anchor in the Snobos YAML: show date `2026-10-14` is episode `383`.
- A show normally occurs every Wednesday and increments the episode number by one, regardless of which co-host produces it. The next show produced by the user is episode `385` on `2026-10-28`.
- Configure skipped show dates (for holidays or off weeks) in YAML. A skipped date does not consume an episode number; subsequent episode numbers advance only for shows that occur.
- Add a CLI flag to override the calculated episode number for a run.
- Include the episode number and show date at the top of every generated file. Use the episode number in generated filenames.

## Sources And Search

- Use Claude's built-in web search tool through the Anthropic API for web discovery.
- Read RSS feeds from 9to5Mac, AppleInsider, and MacRumors.
- Do not use podcast transcripts in v1.
- Put search behind a small provider interface so a dedicated provider such as Tavily or Exa can be substituted later without changing agent prompts or workflow logic.
- Preserve source links when results overlap; deduplicate stories without discarding distinct useful sources.
- Include all discovered candidates relevant to the show segments. Apply topical/date relevance and duplicate handling, but do not rank candidates or editorially reduce them to a shortlist. Do not claim exhaustive coverage of the internet.

## Rundown Format

Write Markdown grouped under these segments, in this order, using the exact headings shown:

1. The Lowdown — 3 Apple stories
2. 2nd String — 1 non-Apple tech story
3. For The Culture — 1 story (Black culture/pop culture)
4. The Hookup — 1 item (consumer safety/tips)

Each candidate includes a headline, a one- or two-sentence summary, source link(s), and date. Use the story's publication date when available; make missing dates explicit rather than inventing one. The counts in the segment headings describe the planned show allocation; Stage 1 remains a comprehensive, unfiltered candidate list and must not truncate candidates to those counts or curate a shortlist.

Save each Stage 1 run to `data/snobos/rundowns/<episode> Rundown.md` (for example, `data/snobos/rundowns/383 Rundown.md`). The rundown directory is generated output and must remain ignored by Git.

## Later Stages (Not In V1 Scope)

- Stage 2 will produce a slate named `<episode> Slate.md` (for example, `383 Slate.md`). It will use the episode number and show date at the top.
- Stage 3 will produce show notes named `<episode> Show Notes.md` (for example, `383 Show Notes.md`), also with the episode number and show date at the top. Stage 3 must follow the existing show notes template; adding a copy of that template to the repository is a prerequisite before Stage 3 begins.
- Stage 2 and Stage 3 are future work and do not change Stage 1's candidate-gathering scope.

## Future Consideration: snobist Show

The snobist Show is a separate 15-minute exclusive show for paying Patreon supporters. It is documented here only as a future consideration; do not design or build it as part of this plan. Open questions for later:

- Does it need its own sourcing or show notes?
- Does it share the main show's reporting window?
- How should its content differ from the main show?

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

- Make the CLI execute a Snobos run and accept the recording/show day plus an optional episode-number override.
- Load the Snobos YAML settings and `configs/snobos.env` secret.
- Keep the direct Anthropic client for v1; do not add LangGraph.
- Define typed, framework-agnostic settings and story data structures, including the episode anchor and skipped show dates.

### Step 2: Search And RSS Sources

- Implement the replaceable web search provider using Claude's built-in API tool, enforcing the configured search cap.
- Implement RSS readers for the three named publications.
- Normalize results to the shared story structure and show the user sample normalized records from each source at this checkpoint.

### Step 3: Weekly Candidate Collection

- Collect candidates for the configured seven-day window ending on the supplied recording day.
- Normalize dates to the configured timezone, deduplicate overlaps while retaining sources, and assign candidates to the four show segments.
- Keep candidate collection comprehensive and unranked; the planned segment counts are not a limit on candidate collection. Report source-level failures without silently presenting a partial run as complete.

### Step 4: Rundown Generation And Output

- Generate the grouped Markdown rundown with headlines, short summaries, links, and dates.
- Put the episode number and show date at the top, write it to `data/snobos/rundowns/<episode> Rundown.md`, and log search count and token usage.

### Step 5: Tests And End-To-End Check

- Add focused tests for config/secrets selection, the reporting window, search limits, RSS parsing, normalization, deduplication, segment grouping, output format/path, and usage/search logging.
- Run the test suite and perform a live smoke test with the user's configured Anthropic key, without exposing the key in output or logs.

## V1 Completion Criteria

- Running the CLI for a recording day uses the Snobos YAML settings and only the Snobos secret file by default.
- The collection window is seven local calendar days, inclusive of the recording day, in `America/New_York`, unless changed in YAML.
- Claude web searches never exceed the configured cap; the default is 10.
- RSS and web candidates are combined, deduplicated with source links retained, and grouped into the four segments without ranking or shortlisting.
- Episode numbering follows the configured anchor and skipped dates, with an explicit CLI override available.
- An episode-numbered Markdown rundown with episode number and show date is written to the required ignored output directory, with search count and token usage logged at run end.