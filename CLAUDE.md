# Stack
- Python 3.14 (stdlib only — no third-party packages unless explicitly requested)
- Node v26 (available but not primary for bootcamp modules)
- No package manager / no requirements.txt unless the module explicitly needs one

# Conventions
- One Python file per module CLI; name it after the primary noun (e.g. `task.py`, not `main.py`)
- snake_case for all functions and variables; no classes unless state genuinely requires it
- Type annotations on every function signature
- Persistence goes to a JSON file in CWD; filename matches the noun (`tasks.json`, etc.)
- Exit codes: 0 = success, 1 = user error (not found / bad args), 2 = internal error (corrupt file / IO failure)
- Error messages to stderr; normal output to stdout
- No docstrings beyond the module-level one-liner

# Commands
- Run: `python3 <module>.py <command> [args]`
- No build step, no install step, no test runner configured — verify behavior by running the script directly
- Lint (if needed): `python3 -m py_compile <file>.py` to catch syntax errors

# Do-not
- Do not add third-party dependencies without asking
- Do not create a `requirements.txt` or `pyproject.toml` unless the module spec calls for it
- Do not split a single-file CLI into multiple files unless the user requests it
- Do not add logging frameworks, config files, or `.env` loading
- Do not renumber task IDs on delete — IDs are append-only and never reused
- Do not commit `tasks.json` or other data files

# Glossary
- **module** — one self-contained exercise directory (module-01, module-02, …); each is independent
- **task** — a to-do item persisted in `tasks.json`; has id, status (`todo`|`done`), created_at (ISO-8601 UTC), text
- **CWD** — the working directory from which the CLI is invoked; where the JSON data file lives
- **loop** — the Plan → Implement → Test → Review → Commit workflow taught in module-01
