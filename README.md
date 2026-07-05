# Skill Router Demo

A small reusable Python library and CLI that routes requested agent skills once
and shares the loaded skill context across subagents. It accepts real subtasks,
loads real `SKILL.md` files from a manifest, produces assignment JSON, and
generates compact preloaded prompts.

## Install Locally

Install the package from this checkout:

```bash
python3 -m pip install -e .
```

This exposes two equivalent local console commands:

```bash
skill-router --help
skill-router-demo --help
```

The package can also be used directly without installation while developing:

```bash
PYTHONPATH=src python3 -m skill_router_demo --help
```

## Use as a Library

```python
from skill_router_demo import (
    build_assignment_plan,
    load_skills_from_manifest,
    load_subtask_request,
)

skills = load_skills_from_manifest("manifests/demo-skills.json")
request = load_subtask_request("examples/subtasks.json")
plan = build_assignment_plan(request, skills)

print(plan["subagents"][0]["skill_id"])
```

## Run the demo

```bash
npm test
npm run test:e2e
```

The default demo command prints a JSON summary:

```json
{
  "cache_hits": 3,
  "naive_loads": 5,
  "routed_loads": 2,
  "subagents": 3
}
```

`naive_loads` counts every skill load request made by the planner, builder,
and tester. `routed_loads` counts the actual unique skill contexts loaded after
the shared router cache is applied.

## Route real subtasks

Use a subtask file with this shape:

```json
{
  "request": "Ship a docs-heavy feature with browser evidence",
  "subtasks": [
    {"id": "read-docs", "task": "Read the PDF and extract requirements"},
    {"id": "test-ui", "task": "Use the browser to verify the UI"}
  ]
}
```

Route it:

```bash
skill-router route examples/subtasks.json
```

The output contains one subagent assignment per subtask:

```json
{
  "subagents": [
    {
      "subtask_id": "read-docs",
      "skill_id": "pdf-reading",
      "skill_hash": "...",
      "selection_mode": "deterministic"
    }
  ]
}
```

Generate preloaded prompts:

```bash
skill-router prompts examples/subtasks.json
```

Each prompt includes only the selected skill context, not the whole skill
catalog. This keeps subagent handoffs short and avoids repeated skill loading.

For ambiguous or no-match subtasks, you can opt into OpenAI-backed fallback
routing:

```bash
OPENAI_API_KEY=... skill-router route examples/subtasks.json --openai-fallback
```

Set `OPENAI_ROUTER_MODEL` or pass `--openai-model` to change the model. Tests
use an injected fake fallback and do not call the OpenAI API.

## Manifest

The manifest points to real skill files:

```json
{
  "skills": [
    {
      "skill_id": "pdf-reading",
      "name": "pdf-reading",
      "triggers": ["pdf", "extract"],
      "required_for": [],
      "path": "../skills/pdf-reading/SKILL.md"
    }
  ]
}
```

The router hashes the actual `SKILL.md` content. If the skill file changes, the
hash changes and the shared cache refreshes.

## ShipSpec Integration

For a ShipSpec-oriented walkthrough, see
[`docs/shipspec-integration.md`](docs/shipspec-integration.md). It shows how to
feed a mission's subtask list through the router and hand compact skill prompts
to planner, builder, tester, reviewer, or release agents.
