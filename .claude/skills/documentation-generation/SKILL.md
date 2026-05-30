---
name: documentation-generation
description: Generate onboarding and handoff docs from a codebase, covering architecture, data flow, and runbook basics.
---

## Purpose

Read a codebase and produce structured documentation suitable for onboarding a new engineer or handing off a service to another team. Output covers architecture overview, key data flows, public API reference (if applicable), local setup steps, and a basic operational runbook.

## When to use it

- When bringing a new engineer onto a project that has no written documentation.
- When handing off a service to another team and they need a starting point.
- When a project's documentation has drifted so far from reality that it must be regenerated from source.
- When preparing for a code audit or compliance review that requires current architecture documentation.

## Prompt body

```text
Generate onboarding and handoff documentation for the project at <PROJECT_ROOT>.

Audience: <AUDIENCE> (default: "a software engineer new to this codebase")
Output file: <OUTPUT_FILE> (default: docs/ONBOARDING.md)

Steps:
1. Read the directory tree (max 3 levels deep) and identify the primary entry points.
2. Read the most important source files to understand architecture (routing, models, services).
   Focus on structure and data flow — do not exhaustively read every file.
3. Identify any existing documentation (README, docs/, comments) and use it to fill gaps,
   but verify claims against actual code before including them.
4. Produce the output document with these sections in order:

---
# <Project Name> — Onboarding Guide

## Overview
<2–4 sentences: what this project does and who uses it>

## Architecture
<Diagram or prose description of the major components and how they communicate>

## Key data flows
<Step-by-step description of the 1–3 most important request/data paths>

## Local setup
<Numbered steps to get the project running locally from a clean machine>

## Running tests
<Command(s) to run the test suite; expected output on success>

## Operational runbook
### How to deploy
<Steps>
### How to check health
<Commands or URLs>
### Common failure modes and fixes
<Bulleted list: symptom → cause → fix>

## Glossary
<Domain terms a newcomer would not know, one line each>
---

Rules:
- Every step must be concrete and runnable — no "configure as appropriate".
- If a section cannot be populated from the codebase, write: "⚠ Not determinable from source — ask the team."
- Do not hallucinate configuration values, URLs, or port numbers; read them from config files.
```

## Expected inputs

- `<PROJECT_ROOT>` — path to the repository root.
- `<AUDIENCE>` — optional; shapes vocabulary and assumed knowledge level.
- `<OUTPUT_FILE>` — optional; path where the generated document should be written.

## Expected outputs

- A single Markdown document written to `<OUTPUT_FILE>`.
- Sections: Overview, Architecture, Key data flows, Local setup, Running tests, Operational runbook, Glossary.
- Sections that cannot be populated from source are flagged with `⚠`.

## Worked example

**Scenario**: Generate onboarding docs for a small REST service at `./api/`.

**Invocation**:
```
/documentation-generation PROJECT_ROOT=./api AUDIENCE="junior backend engineer" OUTPUT_FILE=./api/docs/ONBOARDING.md
```

**Expected output excerpt** (`./api/docs/ONBOARDING.md`):
```markdown
# Notes Service — Onboarding Guide

## Overview
The Notes Service is a REST API that lets users create, retrieve, update, and delete
short text notes. It is consumed by the web frontend and the mobile app.

## Architecture
- `main.py` — FastAPI application entry point; mounts all routers.
- `routers/notes.py` — CRUD endpoints for `/notes`.
- `models.py` — SQLAlchemy ORM models; single `notes` table.
- `schemas.py` — Pydantic request/response models.
- `database.py` — SQLite connection and session factory.

## Key data flows
POST /notes:
1. Request body validated by `NoteCreate` schema.
2. `create_note()` in `routers/notes.py` inserts a row via SQLAlchemy session.
3. Returns 201 with the persisted `Note` object.

## Local setup
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `uvicorn main:app --reload`
```
