# Routing Benchmark

This benchmark measures how well Skill Router assigns skills to a labeled set of
subtasks, and how the ambiguity margin changes how many hard cases are handed to
the LLM fallback. It is reproducible and needs no network access.

Run it:

```bash
PYTHONPATH=src python3 scripts/benchmark.py
```

## What it measures

The dataset ([`benchmarks/labeled_subtasks.json`](../benchmarks/labeled_subtasks.json))
pairs each subtask with the skill a human would assign, over the demo catalog in
[`manifests/demo-skills.json`](../manifests/demo-skills.json).

Two accuracy numbers are reported:

- **Deterministic-only** — keyword routing with no fallback. The honest baseline
  of what the router decides on its own.
- **Fallback upper bound** — the same run, but near-ties and no-match subtasks are
  deferred to a *perfect* fallback (an oracle that always returns the labeled
  answer). This is an upper bound on what a competent LLM fallback could add, not
  a claim about any specific model.

Timing is measured on deterministic routing only, averaged over many passes, so
it never depends on a network call.

## Results

On the 15-subtask reference set:

| Routing | Accuracy | Deferred to fallback |
| --- | --- | --- |
| Deterministic only (no fallback) | 67% | — |
| + fallback, margin `0.00` (exact ties only) | 93% (upper bound) | 4 |
| + fallback, margin `0.15` (default) | 100% (upper bound) | 5 |

Average deterministic routing time: about 10 microseconds per subtask.

## Reading the results

Keyword routing handles clear cases well but misses two kinds of subtask:

- **No-match** — the subtask uses no trigger words (e.g. "Parse the invoice file
  and pull the key figures"). Deterministic routing returns no skill.
- **Near-ties** — two skills score close together (e.g. "Debug the failing
  implementation shown in the browser" scores frontend and TDD within 0.05).
  Deterministic routing picks the higher score, which is sometimes wrong.

The margin is what separates the two fallback rows. At margin `0.00` only exact
score ties are deferred, so one near-tie is still answered incorrectly by keyword
routing. The default margin `0.15` also defers that near-tie, which is why the
upper bound reaches 100%.

The gap between 67% and the fallback rows is the value the LLM fallback can add —
but only to the extent the fallback actually picks correctly. The upper bound
assumes a perfect fallback; a real model will land somewhere between the
deterministic baseline and this ceiling.

This reference set is small and hand-built, so treat the exact percentages as
directional. The benchmark is meant to be extended: add subtasks to the dataset
that reflect your own workflows and re-run.
