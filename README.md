# Skill Router

Route subtasks to preselected agent skills before spawning subagents.

Skill Router is a small Python library and CLI for reducing repeated skill discovery in multi-agent workflows. It reads a manifest of local `SKILL.md` files, routes each subtask to the best skill, hashes the selected skill content, and produces compact subagent assignments or prompts.

## Why

In a multi-subagent workflow, each subagent can end up scanning or reasoning over the same skill catalog independently. That repeats context work and makes routing mistakes harder to audit.

Skill Router moves that decision earlier:

```text
request -> subtasks -> skill-router -> preloaded subagent prompts
```

Each subagent receives one selected skill context and starts by stating why that skill applies.

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

## Install Locally

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

## Subtask Input Format

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

## Skill Manifest Format

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

Use a custom manifest:

```bash
skill-router route path/to/subtasks.json --manifest path/to/skills.json
skill-router prompts path/to/subtasks.json --manifest path/to/skills.json
```

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

## Use As A Library

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

See [`docs/comparison-with-without-router.md`](docs/comparison-with-without-router.md).

## ShipSpec Integration

See [`docs/shipspec-integration.md`](docs/shipspec-integration.md) for a ShipSpec-oriented workflow using planner, builder, tester, reviewer, and release handoffs.

## Repository

GitHub: <https://github.com/smart-route-skills/Skill-Router>
