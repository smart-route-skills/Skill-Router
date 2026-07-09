# Skill Router

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-working%20prototype-brightgreen)](docs/comparison-with-without-router.md)

Route subtasks to preselected agent skills before spawning subagents.

Skill Router is a small Python library and CLI for reducing repeated skill discovery in multi-agent workflows. It reads a manifest of local `SKILL.md` files, routes each subtask to the best skill, hashes the selected skill content, and produces compact subagent assignments or prompts.

## Contents

- [How It Works](#how-it-works)
- [Features](#features)
- [Status](#status)
- [Install](#install)
- [Quickstart](#quickstart)
- [Usage](#usage)
- [Formats](#formats)
- [Optional OpenAI Fallback](#optional-openai-fallback)
- [Verification](#verification)
- [Comparison Evidence](#comparison-evidence)
- [Integrations](#integrations)
- [License](#license)

## How It Works

In a multi-subagent workflow, each subagent can end up scanning or reasoning over the same skill catalog independently. That repeats context work and makes routing mistakes harder to audit.

Skill Router moves that decision earlier:

```text
request -> subtasks -> skill-router -> preloaded subagent prompts
```

Each subagent receives one selected skill context and starts by stating why that skill applies. The broader idea is smart routing for agent skills: choose the right skill once, then hand compact context to each worker.

## Features

- Manifest-based skill catalog
- Real `SKILL.md` file loading
- SHA-256 skill content hashes
- Deterministic trigger routing
- Optional OpenAI-backed fallback routing
- JSON assignment output for subagents
- Compact preloaded prompt generation
- Mismatch and promotion gate helpers
- Local Python library and CLI

## Status

Skill Router is a working local prototype with a reusable Python library, CLI, examples, tests, comparison evidence, a portable Agent Skill package, and a Codex plugin wrapper. It is ready for local experimentation and integration into an external orchestrator.

See [Roadmap](docs/roadmap.md) for the next product steps.

## Install

From the repository checkout:

```bash
git clone https://github.com/smart-route-skills/Skill-Router.git
cd Skill-Router
python3 -m pip install -e .
```

This installs two equivalent commands:

```bash
skill-router --help
skill-router-demo --help
```

If your Python scripts directory is not on `PATH`, use the module form while developing:

```bash
PYTHONPATH=src python3 -m skill_router_demo --help
```

## Quickstart

Run the built-in demo checks:

```bash
npm test
npm run test:e2e
```

Route example subtasks:

```bash
skill-router route examples/subtasks.json
```

Generate compact preloaded prompts:

```bash
skill-router prompts examples/subtasks.json
```

Example route output:

```json
{
  "request": "Ship a docs-heavy feature with browser evidence",
  "subagents": [
    {
      "subtask_id": "read-docs",
      "subtask": "Read the PDF and extract requirements",
      "skill_id": "pdf-reading",
      "skill": "pdf-reading",
      "skill_hash": "43619094b5aa4a163e337e9cec0bcee4440330dbb377173c2001faa8045d98f4",
      "selection_mode": "deterministic",
      "confidence": 0.83,
      "reason": "Selected pdf-reading by deterministic; matched pdf, extract."
    }
  ]
}
```

Example generated prompt includes:

```text
You are assigned this subtask: Read the PDF and extract requirements

Preloaded skill: pdf-reading (pdf-reading)
Skill hash: ...
Selection mode: deterministic
Reason: Selected pdf-reading by deterministic; matched pdf, extract.

Before using it, state why this skill applies.

Compact skill context:
# PDF Reading
...
```

## Usage

### As A CLI

Use a custom manifest with either command:

```bash
skill-router route path/to/subtasks.json --manifest path/to/skills.json
skill-router prompts path/to/subtasks.json --manifest path/to/skills.json
```

### As A Library

```python
from skill_router_demo import (
    build_assignment_plan,
    build_prompt_plan,
    load_skills_from_manifest,
    load_subtask_request,
)

skills = load_skills_from_manifest("manifests/demo-skills.json")
request = load_subtask_request("examples/subtasks.json")

assignments = build_assignment_plan(request, skills)
prompts = build_prompt_plan(request, skills)

print(assignments["subagents"][0]["skill_id"])
print(prompts["prompts"][0]["prompt"])
```

## Formats

### Subtask Input

```json
{
  "request": "Ship a docs-heavy feature with browser evidence",
  "subtasks": [
    {"id": "read-docs", "task": "Read the PDF and extract requirements"},
    {"id": "test-ui", "task": "Use the browser to verify the UI"},
    {"id": "ship-report", "task": "Prepare the ShipSpec report and verification handoff"}
  ]
}
```

### Skill Manifest

The manifest points to real skill files:

```json
{
  "skills": [
    {
      "skill_id": "pdf-reading",
      "name": "pdf-reading",
      "triggers": ["pdf", "extract", "document"],
      "required_for": [],
      "path": "../skills/pdf-reading/SKILL.md"
    }
  ]
}
```

The router reads the referenced `SKILL.md` file and hashes its content. When the skill file changes, the hash changes too, preventing stale skill context from being reused silently.

## Optional OpenAI Fallback

Deterministic routing is the default. For ambiguous or no-match subtasks, opt into OpenAI-backed fallback routing:

```bash
OPENAI_API_KEY=... skill-router route examples/subtasks.json --openai-fallback
```

Choose a model with either:

```bash
OPENAI_ROUTER_MODEL=gpt-5.5 skill-router route examples/subtasks.json --openai-fallback
```

or:

```bash
skill-router route examples/subtasks.json --openai-fallback --openai-model gpt-5.5
```

Tests use injected fake fallback functions and do not call the OpenAI API.

## Verification

Run:

```bash
npm run lint
npm test
npm run typecheck
npm run test:e2e
```

Expected:

- lint exits cleanly
- unit tests pass
- typecheck exits cleanly
- e2e output shows `routed_loads` lower than `naive_loads`

## Comparison Evidence

A side-by-side test compared subagents with and without router preselection:

| Workflow | Time |
| --- | --- |
| With router | About 1m 02s |
| Without router | About 4m 46s |

With router, all three subagents accepted their assigned skill and did not need fallback discovery:

| Subtask | Assigned skill |
| --- | --- |
| `read-docs` | `pdf-reading` |
| `test-ui` | `frontend-testing-debugging` |
| `ship-report` | `shipspec` |

See [`docs/comparison-with-without-router.md`](docs/comparison-with-without-router.md). For a copy/paste Claude Desktop demo, see [`docs/claude-desktop-smoke-test.md`](docs/claude-desktop-smoke-test.md).

## Integrations

Skill Router includes a portable Agent Skill at [`agent-skills/skill-router`](agent-skills/skill-router) and a Codex plugin wrapper at [`plugins/skill-router`](plugins/skill-router). The same `$skill-router` workflow can be used by Claude/Agent Skills-compatible clients and Codex.

### Claude Code Plugin

Skill Router is a Claude Code plugin marketplace. Add the marketplace and install the plugin:

```text
/plugin marketplace add smart-route-skills/Skill-Router
/plugin install skill-router@skill-router
```

The install string is `plugin-name@marketplace-name` (both are `skill-router` here). Pull updates later with `/plugin marketplace update skill-router`.

Marketplace manifest paths:

```text
.claude-plugin/marketplace.json
plugins/skill-router/.claude-plugin/plugin.json
```

### Claude Agent Skill

Fast path for most users:

1. Download `skill-router-agent-skill.zip` from the [latest GitHub release](https://github.com/smart-route-skills/Skill-Router/releases/latest).
2. Open Claude and go to **Customize > Skills**.
3. Upload `skill-router-agent-skill.zip`.
4. Ask Claude to use Skill Router when routing subtasks or generating preloaded agent prompts.

Build the ZIP yourself from source:

```bash
git clone https://github.com/smart-route-skills/Skill-Router.git
cd Skill-Router
python3 scripts/package_agent_skill.py
```

The generated ZIP is written to:

```text
dist/skill-router-agent-skill.zip
```

The ZIP contains this portable skill folder:

```text
skill-router/
├── SKILL.md
└── agents/openai.yaml
```

Marketplace/indexer-friendly skill path:

```text
agent-skills/skill-router/SKILL.md
```

### Codex

Install the Python CLI and local Codex plugin:

```bash
git clone https://github.com/smart-route-skills/Skill-Router.git
cd Skill-Router
python3 -m pip install -e .
python3 scripts/install_codex_plugin.py
```

After install, restart Codex or open a new session, then ask for `$skill-router`.

Codex plugin skill path:

```text
plugins/skill-router/skills/skill-router/SKILL.md
```

### Other Skills-Compatible Clients

Copy the portable skill folder into your client's configured skills directory:

```bash
cp -R agent-skills/skill-router <your-skills-directory>/skill-router
```

Different clients use different skill directories, so check your client's current docs before assuming a path.

The bundled skill is intentionally small: it explains when to use Skill Router, how to call the CLI, what assignment output should contain, and how to verify routed prompts.

See [`docs/agent-skill-install.md`](docs/agent-skill-install.md) for Claude, Codex, and SkillsMP install notes.

### ShipSpec

See [`docs/shipspec-integration.md`](docs/shipspec-integration.md) for a ShipSpec-oriented workflow using planner, builder, tester, reviewer, and release handoffs.

## License

MIT License. See [LICENSE](LICENSE).

## Repository

GitHub: <https://github.com/smart-route-skills/Skill-Router>
