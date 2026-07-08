#!/usr/bin/env python3
"""Install the Skill Router Codex plugin into the local personal marketplace.

For Claude, use scripts/package_agent_skill.py to create a ZIP that can be uploaded in Claude under Customize > Skills."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

PLUGIN_NAME = "skill-router"


def load_marketplace(path: Path) -> dict:
    if not path.exists():
        return {"name": "personal", "interface": {"displayName": "Personal"}, "plugins": []}
    return json.loads(path.read_text())


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the Skill Router Codex plugin locally.")
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument("--plugin-root", default=Path.home() / "plugins", type=Path)
    parser.add_argument("--marketplace", default=Path.home() / ".agents" / "plugins" / "marketplace.json", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="Print the planned install paths without writing files.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    source_plugin = repo_root / "plugins" / PLUGIN_NAME
    destination_plugin = args.plugin_root.expanduser() / PLUGIN_NAME
    marketplace_path = args.marketplace.expanduser()

    if not source_plugin.exists():
        raise SystemExit(f"Missing plugin package: {source_plugin}")

    entry = {
        "name": PLUGIN_NAME,
        "source": {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Productivity",
    }

    if args.dry_run:
        print(f"Would copy: {source_plugin} -> {destination_plugin}")
        print(f"Would update: {marketplace_path}")
        print(json.dumps(entry, indent=2))
        return 0

    args.plugin_root.expanduser().mkdir(parents=True, exist_ok=True)
    marketplace_path.parent.mkdir(parents=True, exist_ok=True)

    if destination_plugin.exists():
        shutil.rmtree(destination_plugin)
    shutil.copytree(source_plugin, destination_plugin)

    marketplace = load_marketplace(marketplace_path)
    marketplace.setdefault("name", "personal")
    marketplace.setdefault("interface", {"displayName": "Personal"})
    marketplace.setdefault("plugins", [])
    marketplace["plugins"] = [p for p in marketplace["plugins"] if p.get("name") != PLUGIN_NAME]
    marketplace["plugins"].append(entry)
    marketplace_path.write_text(json.dumps(marketplace, indent=2) + "\n")

    print("Installed Skill Router Codex plugin.")
    print(f"Plugin: {destination_plugin}")
    print(f"Marketplace: {marketplace_path}")
    print("Restart Codex or open a new session for plugin discovery to refresh.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
