# Codex Plugin Package

Skill Router includes a Codex plugin wrapper at `plugins/skill-router`.

The plugin provides the `$skill-router` skill, which tells Codex how to use the Skill Router CLI to route subtasks once and generate compact preloaded prompts before spawning subagents.

## Skill Path

The marketplace/indexer-friendly skill file is:

```text
plugins/skill-router/skills/skill-router/SKILL.md
```

That `SKILL.md` contains the trigger description, workflow, CLI examples, output expectations, and verification commands.

## SkillsMP

SkillsMP indexes public GitHub repositories that contain `SKILL.md` files. This repository is prepared for that style of discovery because it contains a portable Agent Skill and a Codex plugin skill:

```text
agent-skills/skill-router/
├── SKILL.md
└── agents/openai.yaml

plugins/skill-router/skills/skill-router/
├── SKILL.md
└── agents/openai.yaml
```

Suggested SkillsMP listing summary:

```text
Route subtasks to preselected agent skills before spawning subagents. Generates compact preloaded prompts, hashes skill files for cache safety, and logs routing decisions for review.
```

Suggested tags:

```text
agents, skills, claude, codex, routing, subagents, cli, automation, python
```

## Local Personal Marketplace

From a fresh clone, install the Python CLI and local Codex plugin:

```bash
git clone https://github.com/smart-route-skills/Skill-Router.git
cd Skill-Router
python3 -m pip install -e .
python3 scripts/install_codex_plugin.py
```

The installer copies `plugins/skill-router` to `~/plugins/skill-router` and adds this entry to `~/.agents/plugins/marketplace.json`:

```json
{
  "name": "skill-router",
  "source": {"source": "local", "path": "./plugins/skill-router"},
  "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
  "category": "Productivity"
}
```

Run a dry-run first if you want to inspect the target paths:

```bash
python3 scripts/install_codex_plugin.py --dry-run
```

After install, restart Codex or open a new session for plugin discovery to refresh.

## Verify

From the repository root:

```bash
python3 /Users/mac/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/skill-router
python3 /Users/mac/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/skill-router/skills/skill-router
```
