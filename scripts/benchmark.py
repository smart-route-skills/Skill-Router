#!/usr/bin/env python3
"""Routing benchmark for Skill Router.

Measures how well the router assigns skills to a labeled set of subtasks, and
how the ambiguity margin changes how many hard cases are handed to the LLM
fallback.

Two accuracy numbers are reported:

* Deterministic-only: keyword routing with no fallback. This is the honest
  baseline of what the router decides on its own.
* Fallback upper bound: the same run, but near-ties and no-match subtasks are
  deferred to a *perfect* fallback (an oracle that always returns the labeled
  answer). This is an upper bound on what a competent LLM fallback could add,
  not a claim about any specific model.

Timing is measured on deterministic routing only, so it never depends on a
network call.

Usage:
    PYTHONPATH=src python3 scripts/benchmark.py
    PYTHONPATH=src python3 scripts/benchmark.py --dataset benchmarks/labeled_subtasks.json --runs 2000
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from skill_router.router import (
    SkillRouter,
    Subtask,
    SubtaskRequest,
    load_skills_from_manifest,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "manifests" / "demo-skills.json"
DEFAULT_DATASET = REPO_ROOT / "benchmarks" / "labeled_subtasks.json"


def load_dataset(path: Path) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return list(payload["subtasks"])


def make_request(dataset: list[dict[str, str]]) -> SubtaskRequest:
    return SubtaskRequest(
        request="benchmark",
        subtasks=tuple(Subtask(id=item["id"], task=item["task"]) for item in dataset),
    )


def make_oracle(dataset: list[dict[str, str]]):
    """A fallback that always returns the labeled answer for a subtask."""
    expected_by_task = {item["task"]: item["expected"] for item in dataset}

    def oracle(mission, _skills):
        expected = expected_by_task.get(mission)
        return {"skills": [expected] if expected else []}

    return oracle


def accuracy(assignments, dataset: list[dict[str, str]]) -> float:
    expected_by_id = {item["id"]: item["expected"] for item in dataset}
    hits = sum(
        1 for a in assignments if a.skill_id == expected_by_id.get(a.subtask_id)
    )
    return hits / len(dataset)


def run(manifest: Path, dataset_path: Path, runs: int) -> dict[str, object]:
    skills = load_skills_from_manifest(manifest)
    dataset = load_dataset(dataset_path)
    request = make_request(dataset)
    oracle = make_oracle(dataset)

    baseline = SkillRouter(skills).assign_subtasks(request)
    baseline_accuracy = accuracy(baseline, dataset)

    margins: dict[str, dict[str, object]] = {}
    for margin in (0.0, 0.15):
        assignments = SkillRouter(
            skills, llm_fallback=oracle, ambiguity_margin=margin
        ).assign_subtasks(request)
        deferred = sum(1 for a in assignments if a.selection_mode == "llm_fallback")
        margins[f"{margin:.2f}"] = {
            "accuracy": accuracy(assignments, dataset),
            "deferred_to_fallback": deferred,
        }

    # Timing: deterministic routing only, averaged over `runs` passes.
    router = SkillRouter(skills)
    tasks = [item["task"] for item in dataset]
    start = time.perf_counter()
    for _ in range(runs):
        for task in tasks:
            router.route(task)
    elapsed = time.perf_counter() - start
    per_route_us = (elapsed / (runs * len(tasks))) * 1_000_000

    return {
        "subtasks": len(dataset),
        "deterministic_accuracy": baseline_accuracy,
        "margins": margins,
        "runs": runs,
        "avg_route_us": per_route_us,
        "assignments": [
            {
                "id": a.subtask_id,
                "expected": next(d["expected"] for d in dataset if d["id"] == a.subtask_id),
                "deterministic_pick": a.skill_id,
                "mode": a.selection_mode,
            }
            for a in baseline
        ],
    }


def format_report(result: dict[str, object]) -> str:
    lines = []
    lines.append("Skill Router — routing benchmark")
    lines.append("=" * 40)
    lines.append(f"Subtasks:               {result['subtasks']}")
    lines.append(
        f"Deterministic accuracy: {result['deterministic_accuracy']:.0%} "
        "(keyword routing, no fallback)"
    )
    for margin, stats in result["margins"].items():  # type: ignore[union-attr]
        lines.append(
            f"  margin {margin}: upper-bound accuracy {stats['accuracy']:.0%} "
            f"with {stats['deferred_to_fallback']} subtask(s) deferred to fallback"
        )
    lines.append(
        f"Avg route time:         {result['avg_route_us']:.1f} us/subtask "
        f"({result['runs']} runs)"
    )
    lines.append("")
    lines.append("Per-subtask deterministic decision:")
    for row in result["assignments"]:  # type: ignore[union-attr]
        mark = "ok " if row["deterministic_pick"] == row["expected"] else "MISS"
        pick = row["deterministic_pick"] or "(none)"
        lines.append(
            f"  [{mark}] {row['id']}: expected {row['expected']:<28} "
            f"got {pick:<28} [{row['mode']}]"
        )
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="benchmark")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--runs", type=int, default=2000)
    parser.add_argument("--json", action="store_true", help="Emit raw JSON.")
    args = parser.parse_args(argv)

    result = run(args.manifest, args.dataset, args.runs)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(format_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
