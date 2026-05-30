---
name: claude-md-template
description: Generate a high-quality CLAUDE.md tailored to a target project's stack, conventions, and workflow.
---

## Purpose

Inspect a project's repository and produce a `CLAUDE.md` file that gives Claude Code precise, project-specific guidance. The output covers stack, conventions, commands, and guardrails so Claude Code can assist without repeated clarification.

## When to use it

- When starting work in a new or unfamiliar codebase and `CLAUDE.md` is absent.
- When onboarding a team to Claude Code and you need a shared ground-truth config file.
- When an existing `CLAUDE.md` has grown stale after a major refactor or language migration.
- When you want to codify hard-won project conventions so they survive team turnover.

## Prompt body

```text
You are generating a CLAUDE.md file for the project rooted at <PROJECT_ROOT>.

Steps:
1. Read the directory tree (max 3 levels deep). Note primary language(s), framework(s), and package manager(s).
2. Read any existing config files that reveal conventions: pyproject.toml, package.json, .eslintrc, Makefile, Dockerfile, etc.
3. Read the README if present, but do NOT copy it verbatim — extract only what Claude Code needs to operate.
4. Produce a CLAUDE.md using the structure below. Every section is required; omit bullets that do not apply.

---
# Stack
- <language and version>
- <framework / runtime>
- <package manager and lockfile>

# Conventions
- <naming conventions>
- <file layout rules>
- <type annotation or style rules>
- <persistence / state conventions>
- <exit-code / error-output conventions>

# Commands
- Run: `<command to execute the main entry point>`
- Test: `<command to run the test suite>`
- Lint: `<command to lint or type-check>`
- Build: `<command to build, if applicable>`

# Do-not
- <actions Claude should never take, e.g. "Do not add third-party deps without asking">
- <files or directories that must not be modified>
- <ID / state invariants that must be preserved>

# Glossary
- **<term>**: <definition>
---

Rules:
- Every bullet must be concrete and actionable.
- Do not include placeholder text or TODO comments in the output.
- Do not reference this prompt or mention that the file was AI-generated.
- Output only the CLAUDE.md content — no preamble, no explanation.
```

## Expected inputs

- `<PROJECT_ROOT>` — absolute or relative path to the repository root Claude Code should inspect.
- Read access to the project's config files and directory structure.

## Expected outputs

- A single `CLAUDE.md` file written to `<PROJECT_ROOT>/CLAUDE.md`.
- All four sections (Stack, Conventions, Commands, Do-not) populated with project-specific content.
- Optional Glossary section when domain terms need definition.

## Worked example

**Scenario**: A small FastAPI service at `./api/` has no `CLAUDE.md`.

**Invocation**:
```
/claude-md-template PROJECT_ROOT=./api
```

**Expected output excerpt**:
```markdown
# Stack
- Python 3.12
- FastAPI 0.111 + Uvicorn
- pip / pyproject.toml

# Conventions
- snake_case for all functions and variables
- One router file per resource (e.g. `routers/notes.py`)
- Pydantic models in `schemas/`; ORM models in `models/`

# Commands
- Run: `uvicorn api.main:app --reload`
- Test: `pytest -q`
- Lint: `ruff check .`

# Do-not
- Do not commit the `.env` file
- Do not modify `alembic/versions/` manually
```
