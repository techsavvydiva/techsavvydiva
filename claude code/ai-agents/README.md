# AI Agents Platform

A local, multi-agent AI platform for research, content creation, and personal productivity workflows.

The platform currently defines three branded agents:

| Agent | Purpose | Initial focus |
|---|---|---|
| **Synthesized Future** | Business and strategy research | Market scans, emerging technology briefs, opportunity analysis |
| **TechSavvyDiva** | Personal productivity and technology workflows | Weekly priorities, research, career and app-development support |
| **Snobos** | Apple-focused podcast research and content | Episode research, show-note drafts, content angles |

The platform begins with narrowly scoped, mostly read-only agents. External write actions—such as publishing content, sending email, updating Notion, changing calendars, or creating GitHub issues—will require explicit human approval.

## Architecture

The project uses a shared runtime with separate agent packages.

```text
ai-agents/
├── app/                          # Shared platform code
│   ├── main.py                   # CLI entry point
│   ├── config.py                 # Loads the selected agent configuration
│   ├── llm.py                    # Anthropic client factory
│   ├── graph.py                  # Shared LangGraph workflow helpers
│   ├── models.py                 # Shared Pydantic output schemas
│   ├── storage.py                # Local Markdown/JSON output storage
│   └── tools/                    # Shared, reusable tools
│       ├── web_search.py
│       ├── fetch_page.py
│       └── local_files.py
├── agents/                       # Agent-specific behavior
│   ├── synthesized_future/
│   ├── techsavvydiva/
│   └── snobos/
├── configs/                      # Per-agent environment files
│   ├── synthesized_future.env
│   ├── techsavvydiva.env
│   └── snobos.env
├── data/                         # Agent-generated local output
│   ├── synthesized_future/
│   ├── techsavvydiva/
│   └── snobos/
├── notebooks/                    # Prompt and output experiments
├── tests/                        # Unit and integration tests
└── .vscode/                      # VS Code debug configuration
```

### Design principles

- **Shared platform, separate agents.** Common infrastructure lives in `app/`; brand-specific prompts, tools, and workflows live under `agents/`.
- **One API key per agent.** Each agent uses its own Anthropic API key for attribution, cost tracking, and security isolation.
- **Read-first, write-later.** Initial workflows are research-and-draft only. External side effects require approval.
- **Explicit tool permissions.** Each agent has an allowlist of tools and cannot use another agent’s tools by default.
- **Observable by default.** Tool calls, model interactions, errors, and outputs should be traceable.
- **Human approval for irreversible actions.** Publishing, emailing, deleting, spending, or modifying external systems requires confirmation.

## Tech stack

- **macOS**
- **Visual Studio Code**
- **Python 3.12**, managed locally with `uv`
- **uv** for Python version, virtual-environment, and dependency management
- **LangGraph** for agent orchestration
- **Anthropic Claude API** for model access
- **python-dotenv** for environment configuration
- **Pydantic** for structured outputs
- **SQLite checkpointing** for local agent state
- **MCP** for future tool integrations
- **Claude Code** as the primary AI development assistant
- **GitHub Copilot Free** as an optional in-editor coding assistant

> **Python note:** The Mac’s system Python may be 3.9.6, but this project uses Python 3.12 through `uv`. LangGraph and LangChain require Python 3.10 or newer. The system Python is intentionally left unchanged.

## Local setup

### 1. Verify prerequisites

Open VS Code’s integrated terminal with `Control + \`` and run:

```bash
git --version
uv --version
```

If `uv` is not installed:

```bash
brew install uv
```

Or use the official installer:

```bash
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
```

### 2. Install Python 3.12

Install Python 3.12 for this project:

```bash
uv python install 3.12
```

Verify available Python versions:

```bash
uv python list
```

### 3. Pin the project to Python 3.12

From the repository root:

```bash
uv python pin 3.12
```

This creates or updates `.python-version`:

```text
3.12
```

### 4. Create or recreate the virtual environment

If `.venv` already exists but points to Python 3.9.6, remove and recreate it:

```bash
rm -rf .venv
uv venv --python 3.12
uv sync
```

Verify the project environment:

```bash
uv run python --version
uv run python -c "import sys; print(sys.executable)"
```

Expected output:

```text
Python 3.12.x
/Users/yourname/Developer/ai-agents/.venv/bin/python
```

### 5. Select the interpreter in VS Code

1. Press `Cmd+Shift+P`.
2. Run **Python: Select Interpreter**.
3. Select:

```text
./.venv/bin/python
```

If it is not listed:

1. Choose **Enter interpreter path…**
2. Choose **Find…**
3. Select:

```text
ai-agents/.venv/bin/python
```

The VS Code Status Bar should show:

```text
3.12.x ('.venv': venv)
```

## Dependencies

The core dependencies are:

```bash
uv add langgraph langchain langchain-openai langchain-anthropic
uv add "mcp[cli]"
uv add python-dotenv pydantic
uv add langgraph-checkpoint-sqlite
```

If dependencies are already defined in `pyproject.toml`, install them with:

```bash
uv sync
```

## Agent configuration

Each agent has its own environment file under `configs/`.

### Snobos

`configs/snobos.env`

```env
AGENT_NAME=snobos
ANTHROPIC_API_KEY=sk-ant-your-key-here
MODEL_NAME=claude-sonnet-4-5
DATA_DIR=data/snobos
```

### Synthesized Future

`configs/synthesized_future.env`

```env
AGENT_NAME=synthesized_future
ANTHROPIC_API_KEY=sk-ant-your-key-here
MODEL_NAME=claude-sonnet-4-5
DATA_DIR=data/synthesized_future
```

### TechSavvyDiva

`configs/techsavvydiva.env`

```env
AGENT_NAME=techsavvydiva
ANTHROPIC_API_KEY=sk-ant-your-key-here
MODEL_NAME=claude-sonnet-4-5
DATA_DIR=data/techsavvydiva
```

Use a separate Anthropic API key for each agent. Name the keys clearly in the Anthropic Console, for example:

- `snobos-local`
- `synthesized-future-local`
- `techsavvydiva-local`

## Secrets and Git

Ensure `.gitignore` includes:

```gitignore
.env
configs/*.env
data/
.venv/
__pycache__/
*.pyc
.DS_Store
```

Commit only a placeholder file such as `.env.example`:

```env
AGENT_NAME=snobos
ANTHROPIC_API_KEY=sk-ant-your-key-here
MODEL_NAME=claude-sonnet-4-5
DATA_DIR=data/snobos
```

Never commit real API keys.

## Running an agent

The CLI selects an agent, loads its configuration, and executes a task:

```bash
uv run python app/main.py \
  --agent snobos \
  --task "Research the latest Apple developer platform changes for next week's episode"
```

Other examples:

```bash
uv run python app/main.py \
  --agent synthesized_future \
  --task "Identify emerging opportunities in AI developer platforms"
```

```bash
uv run python app/main.py \
  --agent techsavvydiva \
  --task "Prepare this week's priority review"
```

Outputs are written under the selected agent’s data directory, for example:

```text
data/snobos/2026-10-14-apple-developer-platform-brief.md
```

## Debugging in VS Code

Debug configurations are stored in:

```text
.vscode/launch.json
```

Example:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run Snobos Research Agent",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/app/main.py",
      "console": "integratedTerminal",
      "args": [
        "--agent", "snobos",
        "--task", "Research the latest Apple developer platform changes"
      ]
    },
    {
      "name": "Run Synthesized Future Agent",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/app/main.py",
      "console": "integratedTerminal",
      "args": [
        "--agent", "synthesized_future",
        "--task", "Identify emerging opportunities in AI developer platforms"
      ]
    },
    {
      "name": "Run TechSavvyDiva Agent",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/app/main.py",
      "console": "integratedTerminal",
      "args": [
        "--agent", "techsavvydiva",
        "--task", "Prepare this week's priority review"
      ]
    }
  ]
}
```

To debug:

1. Open `app/main.py`.
2. Set a breakpoint.
3. Press `F5`.
4. Inspect variables, tool arguments, and LangGraph state.

## Build roadmap

### Phase 1: Shared foundation

- [x] Set up macOS development environment
- [x] Configure VS Code
- [x] Install and pin Python 3.12 using `uv`
- [x] Create project virtual environment
- [ ] Create agent configuration loader
- [ ] Create Anthropic client factory
- [ ] Implement web-search tool
- [ ] Implement page-fetch tool
- [ ] Implement local Markdown storage
- [ ] Add structured output models
- [ ] Add logging and error handling
- [ ] Add unit tests

### Phase 2: Snobos agent

- [ ] Define Snobos system prompt and brand voice
- [ ] Build podcast research workflow
- [ ] Generate episode research brief
- [ ] Save Markdown draft locally
- [ ] Add source links and citations
- [ ] Test with multiple Apple-focused topics

### Phase 3: Synthesized Future agent

- [ ] Define business research prompt and output schema
- [ ] Build market and technology research workflow
- [ ] Generate opportunity briefs
- [ ] Save Markdown drafts locally

### Phase 4: TechSavvyDiva agent

- [ ] Define personal productivity prompt and workflow
- [ ] Add read-only research and planning tools
- [ ] Generate weekly priority plans
- [ ] Add approval-gated calendar or task integrations later

### Phase 5: Approvals and integrations

- [ ] Add human-in-the-loop approval workflow
- [ ] Add Notion integration
- [ ] Add social drafting and approval workflow
- [ ] Add calendar integration
- [ ] Add GitHub integration
- [ ] Add scheduled runs
- [ ] Add tracing and evaluation

## Security rules

- Never hard-code API keys in source files, notebooks, prompts, or YAML.
- Never commit `.env`, `configs/*.env`, or generated data.
- Use separate API keys per agent.
- Rotate keys if a machine, repository, or credential file is compromised.
- Give agents read access broadly and write access narrowly.
- Require human approval for all irreversible external actions.
- Avoid unrestricted shell, database, or cloud-admin access.

## Current status

The local macOS development environment is configured with Python 3.12 through `uv`. The repository architecture, three-agent model, per-agent credential strategy, and VS Code debugging approach are defined.

The next implementation milestone is to build the shared foundation and complete the first end-to-end **Snobos** research workflow.