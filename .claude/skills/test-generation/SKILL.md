---
name: test-generation
description: Generate a meaningful test suite for a target file or function, covering happy paths, edges, and failures.
---

## Purpose

Produce a runnable test file for a specified source file or function. Tests cover the happy path, representative edge cases, and expected failure modes. The output uses the project's existing test framework and follows its naming conventions.

## When to use it

- When a new module ships with no tests and coverage needs to be bootstrapped quickly.
- When adding a test suite to legacy code before a refactor to lock in current behavior.
- When a function has complex branching logic that is hard to reason about manually.
- When a PR reviewer asks for tests before approval.

## Prompt body

```text
Generate a test suite for <TARGET_FILE> (function or module: <TARGET_SYMBOL>).

Detection steps (run before writing tests):
1. Identify the test framework already in use in this project (pytest, unittest, Jest, Vitest, etc.).
2. Identify the naming convention for test files and test functions.
3. Read <TARGET_FILE> completely to understand inputs, outputs, side effects, and error cases.

Test coverage requirements:
- At least one happy-path test per public function/method.
- At least one edge-case test per non-trivial branch (empty input, zero, None/null, boundary values).
- At least one failure-mode test for every documented exception or error return.
- If the code does I/O (file, network, DB), stub or mock the I/O layer; do not hit real resources.

Output:
- A single test file following the project's existing file-naming convention.
- Tests must be runnable with the project's standard test command without modification.
- No placeholder tests (e.g., `assert True`).
- Add a one-line comment above each test group explaining what scenario it covers.
```

## Expected inputs

- `<TARGET_FILE>` — path to the source file to test.
- `<TARGET_SYMBOL>` — optional; name of a specific function or class to focus on (defaults to all public symbols).

## Expected outputs

- A single test file placed next to `<TARGET_FILE>` (or in the project's test directory if one exists).
- Tests runnable with zero modification via the project's standard test command.
- Coverage of happy path, edge cases, and error paths for every targeted symbol.

## Worked example

**Scenario**: `./src/parser.py` contains a `parse_csv` function with no existing tests.

**Invocation**:
```
/test-generation TARGET_FILE=./src/parser.py TARGET_SYMBOL=parse_csv
```

**Expected output excerpt** (`./tests/test_parser.py`):
```python
import pytest
from src.parser import parse_csv

# happy path
def test_parse_csv_returns_list_of_dicts():
    data = "name,age\nAlice,30\nBob,25"
    result = parse_csv(data)
    assert result == [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]

# edge cases
def test_parse_csv_empty_string_returns_empty_list():
    assert parse_csv("") == []

def test_parse_csv_header_only_returns_empty_list():
    assert parse_csv("name,age") == []

# failure modes
def test_parse_csv_raises_on_none():
    with pytest.raises(TypeError):
        parse_csv(None)
```
