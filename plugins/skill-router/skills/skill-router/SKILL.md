---
name: skill-router
description: Use when routing requests or subtask lists to preselected agent skills, generating compact subagent assignments or preloaded prompts, reducing repeated skill discovery/loading, or using the local skill-router CLI.
---

# Skill Router

Use Skill Router to choose skills once before spawning or handing off subagents. The router reads a manifest of skill files, hashes each selected `SKILL.md`, emits assignment JSON, and can generate compact prompts that include only the chosen skill context.

## When To Use

Use this skill when the user asks to:

- Route a user request or subtask list to the right skills.
- Generate subagent assignments with `skill_id`, `skill_hash`, confidence, reason, and selection mode.
- Generate preloaded subagent prompts so workers do not scan all skills themselves.
- Verify or demo the Skill Router CLI.
- Reduce repeated skill selection or loading costs in a multi-agent workflow.

Do not use this skill for ordinary single-agent coding tasks that do not involve skill routing or subagent handoff.

## Local Project

The router project can be installed from:

```text
https://github.com/smart-route-skills/Skill-Router
```

When working on Ewent's local checkout, the project usually lives at:

```text
/Users/mac/Dev/skill-router
```

The installed console script may live at:

```text
/Library/Frameworks/Python.framework/Versions/3.14/bin/skill-router
```

If `skill-router` is not on `PATH`, either call the full path or run the module form from the project:

```bash
PYTHONPATH=src python3 -m skill_router_demo --help
```

## Quick Workflow

1. Inspect or create a subtask JSON file with this shape:

```json
{
  "request": "Ship a docs-heavy feature with browser evidence",
  "subtasks": [
    {"id": "read-docs", "task": "Read the PDF and extract requirements"},
    {"id": "test-ui", "task": "Use the browser to verify the UI"}
  ]
}
```

2. Route subtasks to skills:

```bash
skill-router route examples/subtasks.json
```

3. Generate compact preloaded prompts:

```bash
skill-router prompts examples/subtasks.json
```

4. For a custom manifest, pass `--manifest`:

```bash
skill-router route path/to/subtasks.json --manifest path/to/skills.json
```

5. For ambiguous or no-match routes, optionally use OpenAI fallback when an API key is available:

```bash
OPENAI_API_KEY=... skill-router route examples/subtasks.json --openai-fallback
```

## Verification

Before claiming the router works, run from the project checkout:

```bash
npm run lint
npm test
npm run typecheck
npm run test:e2e
```

Expected signs of success:

- Unit tests report all tests passing.
- E2E output includes `routed_loads` lower than `naive_loads`.
- `route` emits one `subagents` assignment per input subtask.
- `prompts` emits one compact prompt per input subtask.

## Output Expectations

Assignment output should include, per subtask:

```json
{
  "subtask_id": "read-docs",
  "skill_id": "pdf-reading",
  "skill_hash": "...",
  "selection_mode": "deterministic",
  "confidence": 0.83,
  "reason": "Selected pdf-reading by deterministic; matched pdf, extract."
}
```

Prompt output should include:

- The assigned subtask.
- The preloaded skill id and hash.
- The selection mode and reason.
- The line: `Before using it, state why this skill applies.`
- Only the selected skill context, not the whole skill catalog.
