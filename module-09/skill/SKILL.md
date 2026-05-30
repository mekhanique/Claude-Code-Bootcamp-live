---
name: notes-api-smoke
description: Boot a single-file FastAPI notes app with uv and assert all 5 CRUD endpoints return the correct HTTP status codes.
---

## Purpose

Start a single-file FastAPI notes application using `uv run` (no pre-installed virtualenv required) and run a curl-based smoke test that verifies the six critical assertions: POST → 201, GET list → 200, GET by id → 200, PATCH → 200, DELETE → 204, and GET on a missing id → 404. Prints PASS or FAIL per check and exits non-zero if any check fails.

## When to use it

- After writing or updating a single-file FastAPI notes service to confirm the happy path works end-to-end before running the full test suite.
- In CI to gate a merge with a fast (< 10 s) smoke check that requires only `uv` on the PATH.
- When handing off the project to a reviewer who wants a one-command sanity check.
- When the unit tests pass but you want to verify the live HTTP layer (routing, serialization, status codes) as well.

## Prompt body

```text
Run a smoke test against a single-file FastAPI notes app.

Inputs:
  APP_DIR   — directory containing the Python module (e.g. ./api)
  APP_MODULE — Python import name of the FastAPI app (e.g. notes:app)
  PORT      — local port to bind (default: 8765)

Steps:
1. Start the server in the background:
     uv run --with fastapi --with uvicorn \
       uvicorn <APP_MODULE> --app-dir <APP_DIR> --port <PORT> --log-level warning &
   Save the PID; register a trap to kill it on exit.

2. Wait up to 10 s for the server to accept connections:
   Poll GET http://localhost:<PORT>/docs every 0.5 s; abort with FAIL if it never responds.

3. Run the following checks in order and print "PASS  <label>" or "FAIL  <label>":
   a. POST /notes with {"title":"smoke","body":"test"} → expect 201; capture the returned id.
   b. GET  /notes                                      → expect 200.
   c. GET  /notes/<id>                                 → expect 200.
   d. PATCH /notes/<id> with {"title":"updated"}       → expect 200.
   e. DELETE /notes/<id>                               → expect 204.
   f. GET  /notes/999                                  → expect 404.

4. Print a summary line: "Results: N passed, M failed."
5. Exit 0 if M == 0; exit 1 otherwise.

Use only bash, curl, and python3 (for JSON parsing) — no additional tools required.
```

## Expected inputs

- `APP_DIR` — path to the directory that contains the FastAPI module file.
- `APP_MODULE` — uvicorn-style module reference (`<filename_without_py>:app`).
- `PORT` — optional port number (default `8765`); must be free on the local machine.

## Expected outputs

- Six lines, each starting with `PASS` or `FAIL`, labelled by endpoint and expected status code.
- A `Results: N passed, M failed.` summary line.
- Exit code `0` on full pass, `1` on any failure.

## Worked example

**Scenario**: Smoke-test the notes app at `module-09/notes.py` on port 8765.

```bash
#!/usr/bin/env bash
set -uo pipefail

APP_DIR="module-09"
APP_MODULE="notes:app"
PORT=8765
BASE="http://localhost:${PORT}"

# Boot server
uv run --with fastapi --with uvicorn \
  uvicorn "${APP_MODULE}" --app-dir "${APP_DIR}" \
  --port "${PORT}" --log-level warning &
SERVER_PID=$!
trap 'kill "${SERVER_PID}" 2>/dev/null; wait "${SERVER_PID}" 2>/dev/null' EXIT

# Wait for readiness (up to 10 s)
READY=0
for _ in $(seq 1 20); do
  curl -sf "${BASE}/docs" >/dev/null 2>&1 && { READY=1; break; }
  sleep 0.5
done
if [ "${READY}" -eq 0 ]; then
  echo "FAIL  server did not start within 10 s"
  exit 1
fi

PASSED=0
FAILED=0

check() {
  local label="$1" expected="$2" actual="$3"
  if [ "${actual}" = "${expected}" ]; then
    echo "PASS  ${label}"
    PASSED=$((PASSED + 1))
  else
    echo "FAIL  ${label}  (expected ${expected}, got ${actual})"
    FAILED=$((FAILED + 1))
  fi
}

# a. POST /notes → 201; capture id
TMPFILE=$(mktemp)
STATUS=$(curl -s -o "${TMPFILE}" -w "%{http_code}" -X POST "${BASE}/notes" \
  -H "Content-Type: application/json" \
  -d '{"title":"smoke","body":"test"}')
check "POST /notes → 201" 201 "${STATUS}"
NOTE_ID=$(python3 -c "import json; print(json.load(open('${TMPFILE}'))['id'])")
rm -f "${TMPFILE}"

# b. GET /notes → 200
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/notes")
check "GET /notes → 200" 200 "${STATUS}"

# c. GET /notes/<id> → 200
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/notes/${NOTE_ID}")
check "GET /notes/${NOTE_ID} → 200" 200 "${STATUS}"

# d. PATCH /notes/<id> → 200
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "${BASE}/notes/${NOTE_ID}" \
  -H "Content-Type: application/json" -d '{"title":"updated"}')
check "PATCH /notes/${NOTE_ID} → 200" 200 "${STATUS}"

# e. DELETE /notes/<id> → 204
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "${BASE}/notes/${NOTE_ID}")
check "DELETE /notes/${NOTE_ID} → 204" 204 "${STATUS}"

# f. GET /notes/999 → 404
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/notes/999")
check "GET /notes/999 → 404" 404 "${STATUS}"

echo ""
echo "Results: ${PASSED} passed, ${FAILED} failed."
[ "${FAILED}" -eq 0 ]
```

**Expected terminal output** (all passing):
```
PASS  POST /notes → 201
PASS  GET /notes → 200
PASS  GET /notes/1 → 200
PASS  PATCH /notes/1 → 200
PASS  DELETE /notes/1 → 204
PASS  GET /notes/999 → 404

Results: 6 passed, 0 failed.
```
