# ShipSpec Skill Route

Mission: package-skill-router-as-a-reusable-local-library-and-cli-with-clean-docs-example

## Routing Rule

- Read Agentic RAG before choosing optional skills.
- Use only skills that match repo evidence, mission text, or retrieved files.
- Do not use random skills just because they are installed.

## Recommended Skills

1. shipspec (required) - Always use the active ShipSpec mission, spec, context pack, and verification workflow.
2. agentic-rag (recommended) - Run `gsd rag "<feature area>"` when file context is weak or the repo has many possible skills.
3. test-driven-development (required) - This is an implementation mission; write or update focused tests before production code.
4. sdach-ai (recommended) - The request looks ticket-driven, so use the delivery item workflow for requirement clarity.

## Context Priority

1. Run `gsd rag "Package skill-router as a reusable local library and CLI with clean docs, examples, and integration guide for ShipSpec"` for cited local retrieval.
2. .gsd/packs/package-skill-router-as-a-reusable-local-library-and-cli-with-clean-docs-example.md
3. .gsd/prompts/package-skill-router-as-a-reusable-local-library-and-cli-with-clean-docs-example.md

## Likely Files

- tests/__pycache__/test_skill_router.cpython-314-pytest-9.0.2.pyc
- tests/test_skill_router.py
- src/skill_router_demo/__pycache__/router.cpython-314.pyc
- src/skill_router_demo/router.py
- skills/shipspec/SKILL.md
- src/skill_router_demo/__init__.py
- src/skill_router_demo/__main__.py
- src/skill_router_demo/__pycache__/__init__.cpython-314.pyc
