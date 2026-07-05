# ShipSpec Context Pack

Use this as a compact, agent-neutral handoff for implementation, review, or follow-up planning.

## Active Change

- Title: Create a Python skill-router demo project in Dev/skill-router that reduces repeated skill selection/loading for subagents
- Slug: create-a-python-skill-router-demo-project-in-dev-skill-router-that-reduces-repea
- Branch: unavailable

## Spec Files

- Proposal: openspec/changes/create-a-python-skill-router-demo-project-in-dev-skill-router-that-reduces-repea/proposal.md
- Tasks: openspec/changes/create-a-python-skill-router-demo-project-in-dev-skill-router-that-reduces-repea/tasks.md
- Acceptance criteria: present
- Verification plan: present

## Validation

- Spec validation: pass
- Ready validation: pass

## Changed Files

- No Git changes detected, or Git is unavailable.

## Likely Files

- src/skill_router_demo/router.py
- tests/test_skill_router.py
- src/skill_router_demo/__init__.py
- src/skill_router_demo/__main__.py
- pyproject.toml

## Evidence Summary

- Evidence file: .agent/evidence/create-a-python-skill-router-demo-project-in-dev-skill-router-that-reduces-repea.md
- Verified: lint passed
- Verified: unit passed
- Verified: typecheck passed
- Verified: e2e passed
- Skipped: None
- Risk: No verification risks detected from configured checks.

## Risk

- Level: low
- no deterministic risks detected

## Human Decisions

- No recorded human decisions.

## Next Action

- Command: gsd release
- Reason: Core planning, verification, review, report, and dashboard artifacts are present.
- Also useful: gsd done
- Also useful: gsd ui
- Also useful: gsd status

## Review Report

- .gsd/reports/create-a-python-skill-router-demo-project-in-dev-skill-router-that-reduces-repea.md

## AI Instructions

- Read the spec files before proposing changes.
- Use the changed files and evidence summary to focus review.
- Call out missing verification, skipped checks, and risky affected areas.
- Keep implementation scoped to the active change.
- Do not deploy or access secrets from this pack.
