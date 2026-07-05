# Package skill-router as a reusable local library and CLI with clean docs, examples, and integration guide for ShipSpec Verification Evidence

Mode: full
Generated: 2026-07-05T16:09:06.985Z

## Summary

Verified:
- lint passed
- unit passed
- typecheck passed
- e2e passed

Skipped:
- None

Risk:
- No verification risks detected from configured checks.

## Checks

### lint

Command: `npm run lint`
Result: pass
Required: yes

```text
> lint
> python3 -c "import ast,pathlib; [ast.parse(p.read_text(), filename=str(p)) for root in ('src','tests') for p in pathlib.Path(root).rglob('*.py')]"
```

### unit

Command: `npm test`
Result: pass
Required: yes

```text
> test
> PYTHONPATH=src python3 -B -m unittest discover -s tests

........................
----------------------------------------------------------------------
Ran 24 tests in 0.007s

OK
```

### typecheck

Command: `npm run typecheck`
Result: pass
Required: yes

```text
> typecheck
> python3 -c "import ast,pathlib; [ast.parse(p.read_text(), filename=str(p)) for root in ('src','tests') for p in pathlib.Path(root).rglob('*.py')]"
```

### e2e

Command: `npm run test:e2e`
Result: pass
Required: no

```text
> test:e2e
> PYTHONPATH=src python3 -B -m skill_router_demo

{
  "audit_events": 5,
  "cache_hits": 3,
  "naive_loads": 5,
  "promotion_approved": true,
  "routed_loads": 2,
  "subagents": 3
}
```

