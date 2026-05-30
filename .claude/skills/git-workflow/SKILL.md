---
name: git-workflow
description: Drive a safe AI-assisted Git flow: branch, commit with conventional messages, review diff, and open a PR.
---

## Purpose

Execute a complete, safe Git development workflow from branch creation through pull-request creation. Enforces conventional commits, verifies the diff before committing, and opens a structured PR. Designed to prevent common AI-assisted coding mistakes: committing unintended files, force-pushing, or skipping review steps.

## When to use it

- When starting work on a new feature or bug fix that should live on its own branch.
- When you want Claude Code to handle the Git mechanics while you focus on the code changes.
- When enforcing consistent commit messages and PR structure across a team.
- When preparing a PR for a change that has already been implemented locally.

## Prompt body

```text
Execute the following Git workflow for the change described as: <CHANGE_DESCRIPTION>

Base branch: <BASE_BRANCH> (default: main)
Branch name: <BRANCH_NAME> (default: derived from CHANGE_DESCRIPTION in kebab-case)

Step 1 — Create branch:
Run: git checkout -b <BRANCH_NAME> <BASE_BRANCH>
Abort and report if the branch already exists.

Step 2 — Show diff for review:
Run: git diff HEAD
List every changed file and its line-count delta.
Do NOT proceed to Step 3 until the diff is confirmed (in interactive mode, prompt the user; in automated mode, proceed).

Step 3 — Stage and commit:
Stage only the files relevant to <CHANGE_DESCRIPTION>. Do NOT use `git add -A` or `git add .`.
Construct a conventional commit message:
  - type: feat | fix | docs | refactor | test | chore
  - scope: optional, derived from changed file or directory name
  - subject: imperative mood, ≤72 characters, no period
  Format: `<type>(<scope>): <subject>`
Run: git commit -m "<message>"
If pre-commit hooks fail, stop and report the failure; do not retry with --no-verify.

Step 4 — Open pull request:
Run: gh pr create --title "<type>(<scope>): <subject>" --body "$(cat <<'EOF'
## Summary
<2-4 bullets describing what changed and why>

## Test plan
- [ ] <verification step 1>
- [ ] <verification step 2>
EOF
)"
Report the PR URL on success.

Safety rules (never override):
- Never force-push.
- Never use --no-verify.
- Never commit files matching: *.env, *.key, *.pem, *secret*, *credential*.
```

## Expected inputs

- `<CHANGE_DESCRIPTION>` — a short description of the change (used to derive branch name and commit message).
- `<BASE_BRANCH>` — optional; the branch to cut from (default: `main`).
- `<BRANCH_NAME>` — optional; override the auto-derived branch name.

## Expected outputs

- A new branch created from `<BASE_BRANCH>`.
- A diff review listing all changed files.
- A conventional-commit message and a completed commit.
- A pull request opened via `gh pr create` with a structured body.
- The PR URL printed on completion.

## Worked example

**Scenario**: Commit and PR a fix for a pagination off-by-one bug in `./api/items.py`.

**Invocation**:
```
/git-workflow CHANGE_DESCRIPTION="fix off-by-one in items pagination" BASE_BRANCH=main
```

**Expected output**:
```
Branch created: fix/off-by-one-in-items-pagination

Changed files:
  api/items.py   +3 / -1

Committing…
[fix/off-by-one-in-items-pagination a1b2c3d] fix(api): correct off-by-one in items pagination

PR created: https://github.com/org/repo/pull/42

PR body:
## Summary
- Fix fence-post error in `get_items` that caused the last item on each page to be omitted.
- No schema or API contract changes.

## Test plan
- [ ] Run `pytest tests/test_items.py -q` — all tests pass.
- [ ] Manually verify last item appears on page 1 with page_size=10.
```
