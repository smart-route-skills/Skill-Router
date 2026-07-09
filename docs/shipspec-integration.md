# ShipSpec Integration Guide

Use `skill-router` to turn a ShipSpec mission's subtasks into compact,
skill-aware agent handoffs.

## 1. Install the Local Package

```bash
python3 -m pip install -e .
```

This installs the `skill-router` CLI and keeps it pointed at the working tree
while you iterate.

## 2. Keep Skills in a Manifest

`manifests/demo-skills.json` maps stable skill IDs to local `SKILL.md` files:

```json
{
  "skill_id": "shipspec",
  "name": "shipspec",
  "triggers": ["mission", "spec", "verification"],
  "required_for": ["ship"],
  "path": "../skills/shipspec/SKILL.md"
}
```

The router reads and hashes the real skill file, so changed skill instructions
produce a new cache key automatically.

## 3. Route ShipSpec Subtasks

Create or reuse a subtask file like `examples/subtasks.json`:

```json
{
  "request": "Ship a docs-heavy feature with browser evidence",
  "subtasks": [
    {
      "id": "read-docs",
      "task": "Read the PDF and extract requirements"
    },
    {
      "id": "ship-report",
      "task": "Prepare the ShipSpec report and verification handoff"
    }
  ]
}
```

Generate assignments:

```bash
skill-router route examples/subtasks.json
```

Generate prompt payloads with only the selected skill context:

```bash
skill-router prompts examples/subtasks.json
```

Use `--manifest path/to/skills.json` when a mission needs a different local
skill catalog.

## 4. Use From Python

```python
from skill_router import build_prompt_plan, load_skills_from_manifest, load_subtask_request

skills = load_skills_from_manifest("manifests/demo-skills.json")
request = load_subtask_request("examples/subtasks.json")
prompt_plan = build_prompt_plan(request, skills)
```

Each prompt asks the subagent to state why the preloaded skill applies before
using the compact skill context.

## 5. Optional Fallback Routing

Deterministic routing is the default. For ambiguous or no-match subtasks, opt in
to OpenAI-backed fallback routing:

```bash
OPENAI_API_KEY=... skill-router route examples/subtasks.json --openai-fallback
```

Tests use injected fallback functions and do not call the OpenAI API.
