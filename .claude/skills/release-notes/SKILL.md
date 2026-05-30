---
name: release-notes
description: Produce structured release notes from a commit range or PR list, grouped by type and audience.
---

## Purpose

Convert a raw list of commits or merged pull requests into polished, audience-ready release notes. Output is grouped by change type (Features, Bug Fixes, Breaking Changes, Deprecations), written in plain language, and ready to paste into a changelog, GitHub release, or internal announcement.

## When to use it

- When cutting a release and the changelog needs to be written from `git log` output.
- When a sprint ends and stakeholders need a summary of what shipped.
- When preparing a GitHub Release and you want structured, human-readable notes.
- When merging a long-running feature branch and need to document what changed.

## Prompt body

```text
Generate release notes for version <VERSION> from the following source:

Source: <SOURCE>
  (Accepted formats: a `git log --oneline` block, a list of PR titles, or a PR range like "PR #42–#67".)
Audience: <AUDIENCE> (default: "end users and developers")
Format: <FORMAT> (default: "markdown")

Steps:
1. Parse every commit message or PR title in <SOURCE>.
2. Classify each item into one of: Feature | Bug Fix | Breaking Change | Deprecation | Internal/Chore.
   - Drop Internal/Chore items from the final output unless explicitly included via INCLUDE_CHORES=true.
3. Write one plain-English bullet per item. Start with a verb ("Add", "Fix", "Remove", "Deprecate").
   - Expand abbreviations; do not paste raw commit hashes.
   - If a PR number is available, append it as `(#NNN)`.
4. Produce the output in this structure:

## <VERSION> — <DATE>

### Breaking Changes
- …

### Features
- …

### Bug Fixes
- …

### Deprecations
- …

Omit any section that has no entries.
5. Add a one-sentence summary at the top: "This release <key highlight>."
```

## Expected inputs

- `<VERSION>` — the release version string (e.g., `v2.4.0`).
- `<SOURCE>` — raw `git log --oneline` output, a list of PR titles, or a PR number range.
- `<AUDIENCE>` — optional; shapes vocabulary (e.g., `"end users"` vs. `"backend engineers"`).
- `<FORMAT>` — optional; `"markdown"` (default) or `"plain text"`.

## Expected outputs

- A structured release notes document with sections for Breaking Changes, Features, Bug Fixes, Deprecations.
- Sections omitted when empty.
- One-sentence release summary at the top.
- Plain-English bullets; no raw commit hashes.

## Worked example

**Scenario**: Cut release `v1.3.0` from the following `git log --oneline` output:

```
a1b2c3d feat: add CSV export to reports
d4e5f6g fix: correct off-by-one in pagination
789abcd chore: upgrade dev dependencies
012def3 feat!: rename /api/v1/items to /api/v2/items (breaking)
345abc6 fix: handle empty search results without 500 error
```

**Invocation**:
```
/release-notes VERSION=v1.3.0 SOURCE="<paste above log>" AUDIENCE="developers"
```

**Expected output**:
```markdown
## v1.3.0 — 2026-05-30

This release adds CSV export, fixes two stability issues, and renames the items API endpoint.

### Breaking Changes
- Rename `/api/v1/items` to `/api/v2/items`; update all client integrations accordingly.

### Features
- Add CSV export to the reports page.

### Bug Fixes
- Fix off-by-one error in pagination that caused the last item to be skipped.
- Handle empty search results without returning a 500 error.
```
