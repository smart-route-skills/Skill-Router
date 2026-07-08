# Claude Desktop Smoke Test

Use this small test to compare a multi-agent workflow **without** Skill Router and **with** Skill Router in Claude Desktop.

The test is self-contained: it includes the same task, subtask list, and mini skill catalog in both prompts. It does not require running the Python CLI.

## Before You Start

Install the Claude skill first:

1. Download `skill-router-agent-skill.zip` from the latest release:

```text
https://github.com/smart-route-skills/Skill-Router/releases/latest
```

2. Open Claude Desktop.
3. Go to **Customize > Skills**.
4. Upload `skill-router-agent-skill.zip`.

Then run the two prompts below in two separate Claude chats.

## Test A: Without Skill Router

Paste this into Claude:

```text
Run this as a multi-agent planning simulation.

Do NOT use Skill Router. Let each subagent decide for itself which skill or skills it needs.

User request:
Ship a small docs-heavy feature: read requirements, verify UI behavior, and prepare a release handoff.

Subtasks:
1. read-docs: Read the PDF and extract requirements.
2. test-ui: Use the browser to verify the UI behavior.
3. ship-report: Prepare the ShipSpec report and verification handoff.

Available skills:
- pdf-reading: Read PDFs, extract requirements, summarize document evidence.
- frontend-testing-debugging: Verify browser UI behavior, inspect UI issues, collect screenshots or test evidence.
- shipspec: Prepare implementation/review/release handoff and verification notes.
- test-driven-development: Write failing tests first, implement, then refactor.
- docx: Prepare Word documents and reports.

For each subagent, report:
- subtask id
- skills used or considered
- why it chose them
- whether skill discovery happened inside the subagent

Then summarize how many total skill-selection decisions happened across all subagents.
```

Expected shape:

```text
read-docs considered pdf-reading, docx, maybe shipspec...
test-ui considered frontend-testing-debugging, test-driven-development...
ship-report considered shipspec, docx...
Skill discovery happened inside each subagent.
```

The exact wording can vary. The important thing is that each subagent makes or explains its own skill choice.

## Test B: With Skill Router

Paste this into a new Claude chat after the Skill Router skill is installed:

```text
Use Skill Router for this multi-agent planning simulation.

Route each subtask to exactly one preselected skill before spawning subagents. Do not let subagents rediscover skills independently.

User request:
Ship a small docs-heavy feature: read requirements, verify UI behavior, and prepare a release handoff.

Subtasks:
1. read-docs: Read the PDF and extract requirements.
2. test-ui: Use the browser to verify the UI behavior.
3. ship-report: Prepare the ShipSpec report and verification handoff.

Available skills:
- pdf-reading: Read PDFs, extract requirements, summarize document evidence.
- frontend-testing-debugging: Verify browser UI behavior, inspect UI issues, collect screenshots or test evidence.
- shipspec: Prepare implementation/review/release handoff and verification notes.
- test-driven-development: Write failing tests first, implement, then refactor.
- docx: Prepare Word documents and reports.

Return:
1. A router table with subtask id, assigned skill, confidence, selection mode, and reason.
2. One compact preloaded prompt per subagent.
3. A final comparison against the without-router version.

Each preloaded prompt must include:
- assigned subtask
- preloaded skill
- reason the skill applies
- this line: Before using it, state why this skill applies.
- fallback discovery needed: no
```

Expected shape:

```text
read-docs -> pdf-reading
test-ui -> frontend-testing-debugging
ship-report -> shipspec

Fallback discovery needed: no
Skill choice happened once in the router, before subagents started.
```

## What Customers Should Notice

| Run | Expected behavior |
| --- | --- |
| Without Skill Router | Each subagent independently considers/selects skills. |
| With Skill Router | A router assigns one skill per subtask first, then subagents receive compact preloaded prompts. |

The point is not that the demo has real PDFs or UI. The point is to show the workflow difference: repeated per-subagent skill discovery versus centralized skill routing.
