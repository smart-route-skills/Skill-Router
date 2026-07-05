# ShipSpec Skill Route

Mission: add-full-skill-router-v2-behavior-with-llm-fallback-explicit-selection-modes-rou

## Routing Rule

- Read Agentic RAG before choosing optional skills.
- Use only skills that match repo evidence, mission text, or retrieved files.
- Do not use random skills just because they are installed.

## Recommended Skills

1. shipspec (required) - Always use the active ShipSpec mission, spec, context pack, and verification workflow.
2. agentic-rag (recommended) - Run `gsd rag "<feature area>"` when file context is weak or the repo has many possible skills.
3. test-driven-development (required) - This is an implementation mission; write or update focused tests before production code.

## Context Priority

1. Run `gsd rag "Add full skill-router v2 behavior with LLM fallback, explicit selection modes, RoutedSkill output, JSONL route logs, strict manifest validation, and configurable mismatch thresholds"` for cited local retrieval.
2. .gsd/packs/add-full-skill-router-v2-behavior-with-llm-fallback-explicit-selection-modes-rou.md
3. .gsd/prompts/add-full-skill-router-v2-behavior-with-llm-fallback-explicit-selection-modes-rou.md

## Likely Files

- tests/test_skill_router.py
- src/skill_router_demo/router.py
- src/skill_router_demo/__init__.py
- src/skill_router_demo/__main__.py
- manifests/demo-skills.json
