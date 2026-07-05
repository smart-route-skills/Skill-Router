# Agentic Context Pack

Local Agentic RAG-style context for an AI coding pass. Generated from repo files and ShipSpec artifacts only.

## Mission

- Title: Upgrade skill-router demo to use manifest-loaded skills, content-hash cache, routed skill confidence, audit logs, mismatch feedback, and promotion gates
- Slug: upgrade-skill-router-demo-to-use-manifest-loaded-skills-content-hash-cache-route
- Branch: unavailable
- Next command: gsd review
- Next reason: Decision-aware review checklist is missing.

## Retrieval Strategy

- Decompose the request into intent tokens from the title and slug.
- Rank local files using likely-file inference, Git changes, project memory, and path/token matches.
- Read top ranked sources first, then inspect adjacent code only when needed.
- Use ShipSpec evidence and validation gaps as the evaluation loop.

## Context Quality

- Score: 100%
- Level: strong
- PASS Ranked local sources: 5 local source files ranked.
- PASS Spec gate: Spec validation passes.
- PASS Project memory: Prior ShipSpec memory is available.
- PASS Test signals: A likely test source is ranked.
- PASS Verification evidence: Verification evidence summary is present.
- PASS Risk posture: Risk level is medium.
- PASS Operator next step: Next command is gsd review.

## Connector Signals

- Local repo: active - 5 ranked local source files.
- ShipSpec memory: active - Learned project signals are available.
- Verification evidence: active - Evidence can guide the evaluation loop.
- External connectors: not configured - Jira, logs, docs, and design connectors can be added later without changing the local context contract.

## Retrieval Loop

- Round 1: derive intent from "Upgrade skill-router demo to use manifest-loaded skills, content-hash cache, routed skill confidence, audit logs, mismatch feedback, and promotion gates" and upgrade-skill-router-demo-to-use-manifest-loaded-skills-content-hash-cache-route.
- Round 2: rank likely files from local project structure, Git state, and ShipSpec memory.
- Round 3: read top sources, then inspect adjacent files only when the quality score is weak or the task is unclear.
- Next refinement: use ranked sources directly, then refresh context after code changes.

## Learning Retrieval

- Common files: None recorded.
- Common checks: None recorded.
- Recent risks: None recorded.
- Ship pattern: None recorded.

## Operator Next Step

- Command: gsd review
- Reason: Decision-aware review checklist is missing.
- Context quality is sufficient for the next AI pass.

## Full Agentic RAG

- Report: .gsd/rag/upgrade-skill-router-demo-to-use-manifest-loaded-skills-content-hash-cache-route.md
- Use `gsd rag "your question"` to refresh full local retrieval.

## Ranked Local Sources

### 1. manifests/demo-skills.json

- Score: 265
- Signals: likely-file, intent-match

```text
2: "skills": [
7: "content": "ShipSpec instructions v1"
12: "content": "TDD instructions v1"
```

### 2. src/skill_router_demo/router.py

- Score: 256
- Signals: likely-file, intent-match

```text
4: import hashlib
12: class Skill:
13: """Metadata used by the demo router to decide which skills to load."""
```

### 3. tests/test_skill_router.py

- Score: 246
- Signals: likely-file, intent-match

```text
5: from skill_router_demo.router import (
6: PromotionGate,
7: Skill,
```

### 4. src/skill_router_demo/__init__.py

- Score: 226
- Signals: likely-file, intent-match

```text
1: """Demo package for routing agent skills once and sharing loaded context."""
3: from .router import (
4: AuditEvent,
```

### 5. src/skill_router_demo/__main__.py

- Score: 226
- Signals: likely-file, intent-match

```text
1: from .router import main
```


## Memory Signals

- Common files: None recorded.
- Common checks: None recorded.
- Recent risks: None recorded.
- Ship pattern: None recorded.

## Evidence Signals

- Verified: lint passed
- Verified: unit passed
- Verified: typecheck passed
- Verified: e2e passed
- Skipped: None
- Risk: No verification risks detected from configured checks.

## Risk Signals

- Level: medium
- next action pending: gsd review

## Evaluation Hints

- Spec validation currently passes.
- Ready validation passes; focus on review/release evidence.
- Risk level: medium.
- After coding, run `gsd verify --full`, `gsd review`, and `gsd validate --ready`.

## AI Handoff

- Read the active proposal and tasks before coding.
- Start from the ranked sources above.
- Keep edits scoped to the active change.
- If retrieved context is weak, inspect neighboring files before editing.
- Do not deploy or access secrets from this context pack.
