# ShipSpec Context Pack

Use this as a compact, agent-neutral handoff for implementation, review, or follow-up planning.

## Active Change

- Title: Add mismatch aggregation over time to skill-router so repeated bad routes block promotion and suggest manifest trigger updates
- Slug: add-mismatch-aggregation-over-time-to-skill-router-so-repeated-bad-routes-block-
- Branch: unavailable

## Spec Files

- Proposal: openspec/changes/add-mismatch-aggregation-over-time-to-skill-router-so-repeated-bad-routes-block-/proposal.md
- Tasks: openspec/changes/add-mismatch-aggregation-over-time-to-skill-router-so-repeated-bad-routes-block-/tasks.md
- Acceptance criteria: present
- Verification plan: present

## Validation

- Spec validation: pass
- Ready validation: pass

## Changed Files

- No Git changes detected, or Git is unavailable.

## Likely Files

- tests/__pycache__/test_skill_router.cpython-314-pytest-9.0.2.pyc
- tests/test_skill_router.py
- src/skill_router_demo/__pycache__/router.cpython-314.pyc
- src/skill_router_demo/router.py
- manifests/demo-skills.json
- src/skill_router_demo/__init__.py
- src/skill_router_demo/__main__.py
- src/skill_router_demo/__pycache__/__init__.cpython-314.pyc

## Evidence Summary

- Evidence file: .agent/evidence/add-mismatch-aggregation-over-time-to-skill-router-so-repeated-bad-routes-block-.md
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

- .gsd/reports/add-mismatch-aggregation-over-time-to-skill-router-so-repeated-bad-routes-block-.md

## AI Instructions

- Read the spec files before proposing changes.
- Use the changed files and evidence summary to focus review.
- Call out missing verification, skipped checks, and risky affected areas.
- Keep implementation scoped to the active change.
- Do not deploy or access secrets from this pack.
