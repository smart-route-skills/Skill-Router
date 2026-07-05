# ShipSpec Context Pack

Use this as a compact, agent-neutral handoff for implementation, review, or follow-up planning.

## Active Change

- Title: Package skill-router as a reusable local library and CLI with clean docs, examples, and integration guide for ShipSpec
- Slug: package-skill-router-as-a-reusable-local-library-and-cli-with-clean-docs-example
- Branch: unavailable

## Spec Files

- Proposal: openspec/changes/package-skill-router-as-a-reusable-local-library-and-cli-with-clean-docs-example/proposal.md
- Tasks: openspec/changes/package-skill-router-as-a-reusable-local-library-and-cli-with-clean-docs-example/tasks.md
- Acceptance criteria: present
- Verification plan: present

## Validation

- Spec validation: pass
- Ready validation: pass

## Changed Files

- No Git changes detected, or Git is unavailable.

## Likely Files

- docs/shipspec-integration.md
- tests/__pycache__/test_skill_router.cpython-314-pytest-9.0.2.pyc
- tests/test_skill_router.py
- src/skill_router_demo/__pycache__/router.cpython-314.pyc
- src/skill_router_demo/router.py
- skills/shipspec/SKILL.md
- src/skill_router_demo/__init__.py
- src/skill_router_demo/__main__.py

## Evidence Summary

- Evidence file: .agent/evidence/package-skill-router-as-a-reusable-local-library-and-cli-with-clean-docs-example.md
- Verified: lint passed
- Verified: unit passed
- Verified: typecheck passed
- Verified: e2e passed
- Skipped: None
- Risk: No verification risks detected from configured checks.

## Risk

- Level: medium
- next action pending: gsd review

## Human Decisions

- No recorded human decisions.

## Next Action

- Command: gsd review
- Reason: Decision-aware review checklist is missing.
- Also useful: gsd validate --ready
- Also useful: gsd report
- Also useful: gsd ui

## Review Report

- .gsd/reports/package-skill-router-as-a-reusable-local-library-and-cli-with-clean-docs-example.md

## AI Instructions

- Read the spec files before proposing changes.
- Use the changed files and evidence summary to focus review.
- Call out missing verification, skipped checks, and risky affected areas.
- Keep implementation scoped to the active change.
- Do not deploy or access secrets from this pack.
