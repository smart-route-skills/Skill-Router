# ShipSpec Skill Route

Mission: create-a-python-skill-router-demo-project-in-dev-skill-router-that-reduces-repea

## Routing Rule

- Read Agentic RAG before choosing optional skills.
- Use only skills that match repo evidence, mission text, or retrieved files.
- Do not use random skills just because they are installed.

## Recommended Skills

1. shipspec (required) - Always use the active ShipSpec mission, spec, context pack, and verification workflow.
2. agentic-rag (recommended) - Run `gsd rag "<feature area>"` when file context is weak or the repo has many possible skills.
3. test-driven-development (required) - This is an implementation mission; write or update focused tests before production code.

## Context Priority

1. Run `gsd rag "Create a Python skill-router demo project in Dev/skill-router that reduces repeated skill selection/loading for subagents"` for cited local retrieval.
2. .gsd/packs/create-a-python-skill-router-demo-project-in-dev-skill-router-that-reduces-repea.md
3. .gsd/prompts/create-a-python-skill-router-demo-project-in-dev-skill-router-that-reduces-repea.md

## Likely Files

- No likely files inferred.
