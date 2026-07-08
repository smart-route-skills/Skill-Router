#!/usr/bin/env python3
"""Create a portable Agent Skill ZIP for Claude and skills-compatible clients."""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path

SKILL_NAME = "skill-router"


def add_tree(zip_file: zipfile.ZipFile, source: Path, archive_root: str) -> None:
    for path in sorted(source.rglob("*")):
        if path.is_file():
            zip_file.write(path, Path(archive_root) / path.relative_to(source))


def main() -> int:
    parser = argparse.ArgumentParser(description="Package Skill Router as a portable Agent Skill ZIP.")
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument("--out", default=None, type=Path, help="Output ZIP path. Defaults to dist/skill-router-agent-skill.zip.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    skill_dir = repo_root / "agent-skills" / SKILL_NAME
    if not skill_dir.exists():
        raise SystemExit(f"Missing skill folder: {skill_dir}")

    output = args.out or (repo_root / "dist" / f"{SKILL_NAME}-agent-skill.zip")
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.exists():
        output.unlink()

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        add_tree(zip_file, skill_dir, SKILL_NAME)

    print(f"Created {output}")
    print("Upload this ZIP in Claude under Customize > Skills, or unpack it into a compatible skills directory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
