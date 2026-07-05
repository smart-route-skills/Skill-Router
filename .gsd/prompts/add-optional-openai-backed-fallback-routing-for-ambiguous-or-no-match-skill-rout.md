Use $shipspec.

Active change: Add optional OpenAI-backed fallback routing for ambiguous or no-match skill-router subtasks while keeping deterministic fake fallback for tests
Slug: add-optional-openai-backed-fallback-routing-for-ambiguous-or-no-match-skill-rout

You are in AI planning mode. Use ShipSpec as the source of truth and prepare a plan before coding.

Read these ShipSpec files:

- openspec/changes/add-optional-openai-backed-fallback-routing-for-ambiguous-or-no-match-skill-rout/proposal.md
- openspec/changes/add-optional-openai-backed-fallback-routing-for-ambiguous-or-no-match-skill-rout/tasks.md
- .gsd/reasoning/add-optional-openai-backed-fallback-routing-for-ambiguous-or-no-match-skill-rout.md
- .gsd/operations/add-optional-openai-backed-fallback-routing-for-ambiguous-or-no-match-skill-rout.md
- .agent/room/add-optional-openai-backed-fallback-routing-for-ambiguous-or-no-match-skill-rout/handoff.md

Human Decisions:

- No recorded human decisions yet.

In AI planning mode:

- Summarize the requested scope in plain language.
- Identify likely affected files and project areas.
- Propose implementation steps.
- Propose focused tests and verification commands.
- Call out risks, assumptions, and open questions.
- Wait for approval before coding.

Safety boundaries:

- Do not deploy.
- Do not access secrets.
- Do not make unrelated refactors.
- Do not edit generated ShipSpec evidence by hand.
- Keep changes scoped to the active ShipSpec change.

After implementation, verify with:

- gsd verify --full
- gsd validate --ready
- gsd report
