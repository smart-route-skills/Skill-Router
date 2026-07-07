# Codex Plugin Package

Skill Router includes a Codex plugin wrapper at `plugins/skill-router`.

The plugin provides the `$skill-router` skill, which tells Codex how to use the Skill Router CLI to route subtasks once and generate compact preloaded prompts before spawning subagents.

## Local Personal Marketplace

A Codex personal marketplace entry has this shape:

```json
{
  "name": "skill-router",
  "source": {"source": "local", "path": "./plugins/skill-router"},
  "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
  "category": "Productivity"
}
```

For a local install, copy `plugins/skill-router` to your Codex plugin directory and add the entry to your personal marketplace file.

## Verify

From the repository root:

```bash
python3 /Users/mac/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/skill-router
python3 /Users/mac/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/skill-router/skills/skill-router
```
