# ShipSpec Skill Route

Mission: add-optional-openai-backed-fallback-routing-for-ambiguous-or-no-match-skill-rout

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

1. Run `gsd rag "Add optional OpenAI-backed fallback routing for ambiguous or no-match skill-router subtasks while keeping deterministic fake fallback for tests"` for cited local retrieval.
2. .gsd/packs/add-optional-openai-backed-fallback-routing-for-ambiguous-or-no-match-skill-rout.md
3. .gsd/prompts/add-optional-openai-backed-fallback-routing-for-ambiguous-or-no-match-skill-rout.md

## Likely Files

- tests/__pycache__/test_skill_router.cpython-314-pytest-9.0.2.pyc
- tests/test_skill_router.py
- src/skill_router_demo/__pycache__/router.cpython-314.pyc
- src/skill_router_demo/router.py
- src/skill_router_demo/__init__.py
- src/skill_router_demo/__main__.py
- src/skill_router_demo/__pycache__/__init__.cpython-314.pyc
- examples/subtasks.json
