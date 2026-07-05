# Reasoning: Upgrade skill-router demo to use manifest-loaded skills, content-hash cache, routed skill confidence, audit logs, mismatch feedback, and promotion gates

Change: upgrade-skill-router-demo-to-use-manifest-loaded-skills-content-hash-cache-route
Generated: 2026-07-04T06:04:47.433Z

## What Matters

- Deliver `Upgrade skill-router demo to use manifest-loaded skills, content-hash cache, routed skill confidence, audit logs, mismatch feedback, and promotion gates` against the active ShipSpec contract.
- Keep acceptance criteria aligned with implementation evidence.
- Use the recorded verification plan as the minimum bar.

## Project Signals

- Runtime: node
- Package manager: npm
- Framework: unknown
- Test runner: unknown
- E2E: none

## Likely Affected Areas

- API/backend surface
- Database/schema surface

## Risks

- Recent loop next actions should be reviewed.

## Recommended Workflow

- gsd validate
- gsd verify --full
- gsd reflect
- gsd loop
- gsd memory

## Required Verification

- npm run lint
- npm test
- npm run typecheck
- npm run test:e2e
- gsd verify --full
- gsd validate --ready

## Questions

- Which project conventions should guide implementation?

## Safety

- Reasoning is local-only and deterministic.
- No network calls are made.
- No shell commands are executed.
- No code edits or workflow mutations are performed.
- File reads are bounded to small ShipSpec memory artifacts.
