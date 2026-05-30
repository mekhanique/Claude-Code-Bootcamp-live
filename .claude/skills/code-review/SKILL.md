---
name: code-review
description: Review a diff or file against a rubric and surface correctness bugs, unsafe AI output, and style violations.
---

## Purpose

Run a structured code review against a configurable rubric, flag correctness bugs, identify unsafe or hallucinated AI output, and emit a prioritized finding list with line references. Designed to complement automated linting with judgment-level checks that tools miss.

## When to use it

- Before merging a pull request that contains AI-generated or AI-assisted code.
- When a colleague asks for a second opinion on a non-trivial change.
- After a large refactor to verify behavior is preserved and no regressions were introduced.
- When a diff touches security-sensitive paths (auth, input parsing, serialization).

## Prompt body

```text
You are performing a structured code review on the diff or file provided as <TARGET>.

Review scope: <SCOPE> (default: "correctness, security, style")

Rubric — evaluate each item as YES / NO / N/A with a one-line rationale:
1. Logic correct: does the code do what its name and comments imply?
2. Edge cases handled: nulls, empty collections, out-of-range values, concurrent access.
3. No unsafe AI output: no hallucinated API calls, invented library methods, or fabricated constants.
4. Input validated at system boundaries (user input, external API responses).
5. No secrets or credentials hard-coded.
6. Error paths exit cleanly with appropriate codes or exceptions.
7. Naming is clear and consistent with surrounding code.
8. No dead code, commented-out blocks, or TODO stubs left behind.

After the rubric, emit a FINDINGS section:
- One bullet per finding, format: `[SEVERITY] file:line — description`.
- SEVERITY is one of: BLOCKER | MAJOR | MINOR | NIT.
- BLOCKERs and MAJORs must include a suggested fix.
- If no findings, output: "No findings. Review passed."

Do not summarize what the code does. Jump straight to the rubric.
```

## Expected inputs

- `<TARGET>` — a file path, a `git diff` output, or a PR number (if GitHub CLI is available).
- `<SCOPE>` — optional comma-separated subset of review areas (e.g., `"security, correctness"`).

## Expected outputs

- A completed rubric table (YES / NO / N/A + rationale per item).
- A `FINDINGS` section with severity-tagged, line-referenced bullets.
- Suggested fixes for every BLOCKER and MAJOR finding.

## Worked example

**Scenario**: A new `auth.py` was added to a web service. Review it for correctness and security.

**Invocation**:
```
/code-review TARGET=./auth.py SCOPE="correctness, security"
```

**Expected output excerpt**:
```
Rubric:
1. Logic correct          YES  — JWT decode path matches the sign path.
2. Edge cases handled     NO   — expired token raises KeyError, not AuthError.
3. No unsafe AI output    YES  — all library calls match PyJWT 2.x API.
4. Input validated        NO   — `username` from request body is passed unsanitized to the SQL query.
5. No hard-coded secrets  YES
6. Error paths clean      NO   — line 42 swallows the exception silently.
7. Naming clear           YES
8. No dead code           YES

FINDINGS:
- [BLOCKER] auth.py:38 — SQL query built with f-string; use parameterized query instead.
- [MAJOR]   auth.py:42 — bare `except:` hides token expiry errors; catch `jwt.ExpiredSignatureError`.
- [MINOR]   auth.py:14 — expired token returns 500; should return 401.
```
