# Skill Router Comparison

## Conclusion

`skill-router` reduced repeated skill discovery by routing subtasks first and giving each subagent a preselected skill.

## Results

| Subtask | Assigned skill |
| --- | --- |
| `read-docs` | `pdf-reading` |
| `test-ui` | `frontend-testing-debugging` |
| `ship-report` | `shipspec` |

All subagents agreed the assigned skill applied, and fallback discovery was not needed.

## Timing

| Workflow | Time |
| --- | --- |
| With router | About 1m 02s |
| Without router | About 4m 46s |
