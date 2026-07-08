# Agent Skill Install

Skill Router is packaged for both Claude/Agent Skills-compatible clients and Codex.

## Portable Agent Skill

Canonical skill path:

```text
agent-skills/skill-router/SKILL.md
```

This folder follows the open Agent Skills shape: a skill directory containing `SKILL.md`, plus optional metadata under `agents/`.

## Claude.ai

Fast path for most users:

1. Download `skill-router-agent-skill.zip` from the latest GitHub release:

```text
https://github.com/smart-route-skills/Skill-Router/releases/latest
```

2. Upload the ZIP in Claude under **Customize > Skills**.

Build the ZIP yourself from source:

```bash
git clone https://github.com/smart-route-skills/Skill-Router.git
cd Skill-Router
python3 scripts/package_agent_skill.py
```

The generated ZIP is written to:

```text
dist/skill-router-agent-skill.zip
```

The ZIP contains:

```text
skill-router/
├── SKILL.md
└── agents/openai.yaml
```

## Claude Code And Other Skills-Compatible Clients

For local clients that read skills from a filesystem directory, copy the portable skill folder into the client's configured skills directory:

```bash
cp -R agent-skills/skill-router <your-skills-directory>/skill-router
```

Different clients use different skill directories, so check your client's current documentation before assuming a path.

## Codex

Install the Python CLI and local Codex plugin:

```bash
git clone https://github.com/smart-route-skills/Skill-Router.git
cd Skill-Router
python3 -m pip install -e .
python3 scripts/install_codex_plugin.py
```

The Codex installer copies `plugins/skill-router` to `~/plugins/skill-router` and updates `~/.agents/plugins/marketplace.json`.

Run a dry-run first if you want to inspect the target paths:

```bash
python3 scripts/install_codex_plugin.py --dry-run
```

## SkillsMP

SkillsMP indexes public GitHub repositories that contain `SKILL.md` files. Use this repository URL:

```text
https://github.com/smart-route-skills/Skill-Router
```

Preferred skill path for marketplace/indexer discovery:

```text
agent-skills/skill-router/SKILL.md
```

Suggested listing summary:

```text
Route subtasks to preselected agent skills before spawning subagents. Generates compact preloaded prompts, hashes skill files for cache safety, and logs routing decisions for review.
```

Suggested tags:

```text
agents, skills, claude, codex, routing, subagents, cli, automation, python
```
