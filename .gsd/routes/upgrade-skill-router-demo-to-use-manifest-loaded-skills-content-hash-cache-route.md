# ShipSpec Skill Route

Mission: upgrade-skill-router-demo-to-use-manifest-loaded-skills-content-hash-cache-route

## Routing Rule

- Read Agentic RAG before choosing optional skills.
- Use only skills that match repo evidence, mission text, or retrieved files.
- Do not use random skills just because they are installed.

## Recommended Skills

1. shipspec (required) - Always use the active ShipSpec mission, spec, context pack, and verification workflow.
2. agentic-rag (recommended) - Run `gsd rag "<feature area>"` when file context is weak or the repo has many possible skills.
3. test-driven-development (required) - This is an implementation mission; write or update focused tests before production code.

## Context Priority

1. Run `gsd rag "Upgrade skill-router demo to use manifest-loaded skills, content-hash cache, routed skill confidence, audit logs, mismatch feedback, and promotion gates"` for cited local retrieval.
2. .gsd/packs/upgrade-skill-router-demo-to-use-manifest-loaded-skills-content-hash-cache-route.md
3. .gsd/prompts/upgrade-skill-router-demo-to-use-manifest-loaded-skills-content-hash-cache-route.md

## Likely Files

- src/skill_router_demo/router.py
- tests/test_skill_router.py
- src/skill_router_demo/__init__.py
- src/skill_router_demo/__main__.py
