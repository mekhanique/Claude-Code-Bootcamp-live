---
name: best-of-n
description: Run a Best-of-N solution-comparison workflow and emit a tradeoff matrix to select the strongest candidate.
---

## Purpose

Generate N independent solutions to a stated problem, evaluate each against a shared rubric, and produce a tradeoff matrix that identifies the best candidate with justification. Useful when the solution space is large or when you want to surface non-obvious approaches before committing to one.

## When to use it

- When a design decision has multiple viable implementations and you want an objective comparison.
- When you are unsure which algorithm, data structure, or architecture fits a given constraint set.
- When a team wants to avoid anchoring on the first solution proposed.
- When a proof-of-concept needs to be evaluated before a full implementation.

## Prompt body

```text
Run a Best-of-<N> comparison for the following problem:

Problem statement: <PROBLEM>
Constraints: <CONSTRAINTS>
N (number of candidates): <N> (default: 3)
Evaluation criteria: <CRITERIA> (default: "correctness, performance, readability, maintainability")

Step 1 — Generate candidates:
Produce exactly <N> distinct solutions. Label them Candidate A, Candidate B, … Candidate N.
Each candidate must be a complete, runnable implementation — no pseudocode, no stubs.
Candidates must differ in approach (different algorithm, data structure, or abstraction), not just style.

Step 2 — Evaluate:
Score each candidate on each criterion from 1 (poor) to 5 (excellent).
Produce a markdown table:

| Criterion        | Candidate A | Candidate B | … |
|-----------------|-------------|-------------|---|
| Correctness     | x/5         | x/5         | … |
| Performance     | x/5         | x/5         | … |
| Readability     | x/5         | x/5         | … |
| Maintainability | x/5         | x/5         | … |
| **Total**       | **xx/20**   | **xx/20**   | … |

Step 3 — Recommendation:
State the winning candidate. Justify in 2–3 sentences referencing the matrix.
Optionally note a "runner-up" if it dominates on a specific constraint.
```

## Expected inputs

- `<PROBLEM>` — a clear problem statement (function signature + behavior description works well).
- `<CONSTRAINTS>` — performance budget, language version, dependency limits, etc.
- `<N>` — number of candidates (2–5 recommended; default 3).
- `<CRITERIA>` — optional custom evaluation criteria list.

## Expected outputs

- N complete, runnable candidate implementations.
- A scored tradeoff matrix in markdown table format.
- A written recommendation identifying the winning candidate and rationale.

## Worked example

**Scenario**: Compare 3 ways to deduplicate a list of strings in Python while preserving insertion order.

**Invocation**:
```
/best-of-n PROBLEM="deduplicate a list of strings, preserving insertion order" CONSTRAINTS="Python 3.10+, stdlib only" N=3
```

**Expected output excerpt**:

Candidate A — `dict.fromkeys`:
```python
def dedup(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))
```

Candidate B — manual set tracking:
```python
def dedup(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
```

Candidate C — `collections.OrderedDict`:
```python
from collections import OrderedDict
def dedup(items: list[str]) -> list[str]:
    return list(OrderedDict.fromkeys(items))
```

| Criterion        | A (dict.fromkeys) | B (set tracking) | C (OrderedDict) |
|-----------------|-------------------|-----------------|-----------------|
| Correctness     | 5/5               | 5/5             | 5/5             |
| Performance     | 5/5               | 4/5             | 4/5             |
| Readability     | 5/5               | 3/5             | 4/5             |
| Maintainability | 5/5               | 3/5             | 4/5             |
| **Total**       | **20/20**         | **15/20**       | **17/20**       |

**Recommendation**: Candidate A (`dict.fromkeys`) wins on all criteria. It is idiomatic Python 3.7+, O(n), and requires no extra imports.
