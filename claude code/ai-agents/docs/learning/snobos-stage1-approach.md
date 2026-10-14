# Snobos Stage 1: Build Steps and Reasoning

This doc explains **how** Stage 1 (Sourcing) of the Snobos agent is built and **why** it's built that way. Snobos is the reference implementation for this repo. The techsavvydiva and synthesized_future agents will follow the same pattern, built hands-on.

Related docs:
- `docs/plans/snobos-v1.md`: what Stage 1 must do
- `docs/architecture.md`: how the system fits together
- `docs/learning/snobos-build-log.md`: what actually happened during the build
- `docs/learning/agent-playbook.md`: the reusable guide for building the next agents (written at the end of Stage 1)

---

## The core pattern

Every agent in this repo follows five principles:

1. **Deterministic code for anything checkable.** Dates, URLs, file formats, and counts are handled by plain code with tests, not by the model.
2. **The model only for judgment.** Use Claude where a human would have to think: summarizing, deciding relevance, matching content to a story, assigning a segment.
3. **One normalized data shape.** Every source produces the same record format, so later steps only handle one kind of data.
4. **Interfaces around external services.** Search providers, feeds, and APIs sit behind small interfaces so they can be swapped without rewriting the agent.
5. **A human checkpoint before anything matters.** The agent proposes and a human approves. Nothing is published or sent without review.

---

## Stage 1 steps

### Step 1: CLI, config loading, and show-window calculation

**What gets built**
- A command-line entry point to run the agent for a given show date
- Loading of the Snobos YAML (model, settings, rotation, episode anchor) and the `snobos.env` secret
- Show-window math: previous show Wednesday through the show date, America/New_York
- Episode-number calculation from the anchor (episode 383 on Oct 14, 2026), with skipped-week handling and a manual override

**Why it's built this way**
- This is plumbing with exact right answers, so it's built first and tested without calling the model.
- If the window or episode number is wrong, every later step is wrong. Catching that here is cheap.
- Config lives in YAML (versioned, reviewable) and secrets live in env files (never committed). Keeping them separate means you can change behavior without touching secrets and share config without leaking keys.

**Reusable for other agents:** config loading, env/secret loading, and the CLI structure.

---

### Step 2: RSS adapters and normalized story records

**What gets built**
- Feed readers for 9to5Mac, AppleInsider, and MacRumors
- A shared story record: headline, summary, publish date, source link(s), source name
- Filtering to the show window

**Why it's built this way**
- RSS is structured, reliable, and free. It covers the core Apple sources with no model cost.
- Normalizing into one record early means verification, dedup, and output each handle only one shape of data.
- Testing with saved feed samples (fixtures) instead of live feeds keeps tests fast and repeatable.

**Reusable for other agents:** the adapter pattern and the idea of a normalized record. Each agent defines its own record fields.

---

### Step 3: Web search adapter

**What gets built**
- Claude's built-in web search behind the same adapter interface as RSS
- Searches for the segments RSS doesn't cover: 2nd String (non-Apple tech), For The Culture, The Hookup
- A configurable cap on searches per run, plus logging of tokens and search count

**Why it's built this way**
- This is the first step that calls the model, so it's isolated, measured, and capped.
- The interface means a dedicated provider (Tavily, Exa, Brave) can replace Claude's search later without changing the rest of the agent.
- Cost logging from day one tells you what a weekly run actually costs before you rely on it.

**Reusable for other agents:** the search interface, the cost guardrails, and usage logging.

---

### Step 4: Verification, deduplication, and segment grouping

**What gets built**
- Verification that each source link resolves, the content matches the story, and the publish date falls inside the window
- Deduplication of stories covered by multiple outlets, keeping all source links
- Assignment of each story to a segment: The Lowdown, 2nd String, For The Culture, The Hookup
- Flags on stories that fail verification, instead of silently dropping them

**Why it's built this way**
- This step separates what the model *claims* from what's *true*. Models can produce plausible but wrong links or dates, so they get checked.
- Code checks what code can check (link resolves, date in range). The model handles judgment (does this page match this story, which segment fits).
- Flagging instead of dropping keeps you informed. You decide what to do with an unverified story.

**Reusable for other agents:** the verification approach. Any agent that cites sources needs it.

---

### Step 5: Markdown rundown output and live run

**What gets built**
- A rundown file at `data/snobos/rundowns/<episode> Rundown.md` (gitignored), grouped by segment, with headline, summary, sources, date, and verification status per story
- A live run for episode 383 (window Oct 7–14, 2026)

**Why it's built this way**
- The output is something a human can review in minutes, not raw data.
- Testing against episode 383, a week where the show notes already exist, gives a known right answer. If the stories you actually picked appear in the rundown, sourcing works.
- Rundowns are outputs, not source code, so they stay out of git.

**Reusable for other agents:** the review-ready output pattern and testing against a known answer.

---

## Working rules for every step

- Plan before code: the approach is explained before anything is written.
- One step at a time, with a checkpoint after each: test, review, commit, push.
- No env file contents are ever read, printed, or committed. Check `git status` before every commit.
- Update the plan docs whenever a decision changes.

---

## What comes after Stage 1

- **Stage 2, Slate:** a recommended pick plus 2 alternates per slot, for approval
- **Stage 3, Show notes:** title, lead-in, and verified source link per story, from the approved slate only, following the show notes template and the `<episode> Show Notes` naming
- **V2:** Google Docs output, Streamlabs scheduling, Patreon notification, scheduled runs
- **V3:** publishing to snoboscast.com, YouTube, Apple Podcasts, and Spotify, and teasers to Facebook, Threads, TikTok, and Instagram

Each stage builds only on a stage that already works.
