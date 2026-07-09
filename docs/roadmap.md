# Roadmap

Skill Router is intentionally small: route skills once, preload workers with compact context, and make routing decisions auditable.

## Done

- Manifest-loaded skill catalog
- Real `SKILL.md` file loading
- SHA-256 skill content hashes
- Deterministic trigger routing
- Optional OpenAI-backed fallback hook
- Margin-based fallback for near-tie routing
- Subagent assignment JSON
- Compact preloaded prompt generation
- Comparison evidence for with-router vs without-router runs
- Reproducible routing-accuracy benchmark
- Claude Code plugin and marketplace
- Continuous integration on Python 3.11 and 3.12
- MIT license and GitHub-facing README

## Next

- Add a packaged release workflow for versioned builds.
- Add more realistic example manifests for common pipelines such as PDF -> analysis -> chart -> report -> email.
- Add richer route metrics: selection mode counts, fallback counts, and mismatch summaries.
- Add a minimal integration guide for external orchestrators.

## Later

- Support multi-skill assignments when one subtask truly needs more than one skill.
- Add configurable routing policies per workflow.
- Add persistent mismatch aggregation over time.
- Explore a plugin package for easier Codex installation.
