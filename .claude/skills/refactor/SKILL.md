---
name: refactor
description: Refactor a target file with stated constraints, preserve observable behavior, and emit a before/after diff plan.
---

## Purpose

Apply a focused refactor to a target file under explicit constraints (e.g., "extract function", "reduce nesting", "replace magic numbers"). Before touching code, emit a diff plan describing every intended change so the user can review intent before execution. Behavior must be identical after the refactor.

## When to use it

- When a function exceeds a complexity or length threshold and needs to be broken up.
- When duplication has accumulated and a shared abstraction is now clearly justified.
- When naming is misleading or inconsistent and must be aligned with surrounding conventions.
- When a module needs to shed dead code, unused imports, or leftover debugging artifacts.

## Prompt body

```text
Refactor <TARGET_FILE> under the following constraints:

Constraints: <CONSTRAINTS>
Preserve: observable behavior, public API signatures, exit codes, and output format.
Forbidden: adding new features, changing behavior, adding dependencies not already present.

Step 1 — Read and analyze:
Read <TARGET_FILE> completely. Identify every location that must change to satisfy the constraints.

Step 2 — Emit a diff plan (BEFORE making any edits):
List every intended change as a bullet:
- [ACTION] location — reason
Where ACTION is one of: EXTRACT | RENAME | INLINE | DELETE | REORDER | SIMPLIFY

Step 3 — Wait for confirmation.
(In automated mode, skip to Step 4 immediately.)

Step 4 — Apply changes:
Edit <TARGET_FILE> in the order listed in the diff plan.
After all edits, run `<VERIFY_COMMAND>` to confirm behavior is preserved.
Report: "Refactor complete. <N> changes applied. Verification: PASSED / FAILED."

If verification fails, revert and report which change caused the regression.
```

## Expected inputs

- `<TARGET_FILE>` — path to the file to refactor.
- `<CONSTRAINTS>` — what to do, e.g., `"extract any function longer than 30 lines"`, `"replace all magic numbers with named constants"`.
- `<VERIFY_COMMAND>` — command to run after the refactor to confirm correctness (e.g., `pytest -q`, `node test.js`).

## Expected outputs

- A diff plan (bulleted list of `[ACTION] location — reason`) emitted before any edits.
- The refactored `<TARGET_FILE>` with all planned changes applied.
- A verification result line: `Refactor complete. N changes applied. Verification: PASSED`.

## Worked example

**Scenario**: `./src/report.py` has a 90-line `generate_report` function. Extract sub-functions and replace magic numbers.

**Invocation**:
```
/refactor TARGET_FILE=./src/report.py CONSTRAINTS="extract functions longer than 25 lines; replace magic numbers with named constants" VERIFY_COMMAND="pytest tests/test_report.py -q"
```

**Expected diff plan output**:
```
Diff plan:
- [EXTRACT]  generate_report:12-38  — filter logic into _filter_records(records, cutoff)
- [EXTRACT]  generate_report:40-72  — formatting logic into _format_rows(records)
- [RENAME]   generate_report:8      — magic literal 90 → MAX_REPORT_ROWS
- [RENAME]   generate_report:25     — magic literal 0.15 → TAX_RATE
- [DELETE]   generate_report:88-90  — commented-out debug print block

Applying changes…
Refactor complete. 5 changes applied. Verification: PASSED
```
