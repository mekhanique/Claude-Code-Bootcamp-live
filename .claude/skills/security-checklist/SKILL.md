---
name: security-checklist
description: Run a security review on a project or diff against the OWASP Top 10 and emit a prioritized finding list.
---

## Purpose

Evaluate a target file, diff, or project directory against the OWASP Top 10 and common secure-coding principles. Produce a checklist of pass/fail items and a prioritized list of findings with remediation guidance. Designed to catch issues that automated SAST tools commonly miss due to insufficient context.

## When to use it

- Before merging any change that touches authentication, authorization, input handling, or data storage.
- When shipping a new API endpoint or user-facing form.
- When conducting a pre-release security sweep of a service.
- When onboarding to a legacy codebase to identify its highest-risk areas quickly.

## Prompt body

```text
Run a security review on <TARGET> against the OWASP Top 10 (2021 edition).

Target: <TARGET> (file path, directory, or git diff)
Depth: <DEPTH> (default: "standard"; options: "quick" | "standard" | "deep")

Checklist — mark each item PASS / FAIL / N/A with a one-line rationale:

A01 Broken Access Control
  - Authorization checks present on every protected route/function.
  - Principle of least privilege applied to roles and permissions.

A02 Cryptographic Failures
  - No secrets, tokens, or credentials hard-coded or logged.
  - Sensitive data encrypted at rest and in transit.

A03 Injection
  - All database queries use parameterized statements or ORMs.
  - Shell/OS commands constructed without user-controlled input.
  - Template rendering uses auto-escaping.

A04 Insecure Design
  - Rate limiting or throttling in place for sensitive operations.
  - No business-logic bypasses (e.g., negative prices, skipped steps).

A05 Security Misconfiguration
  - Debug mode / verbose error messages disabled in production paths.
  - Default credentials or sample configs removed.

A06 Vulnerable and Outdated Components
  - Third-party dependencies pinned; no known CVEs in direct dependencies.

A07 Identification and Authentication Failures
  - Session tokens have appropriate expiry and are invalidated on logout.
  - Password storage uses a strong adaptive hash (bcrypt, argon2).

A08 Software and Data Integrity Failures
  - Deserialization of untrusted data avoided or sandboxed.

A09 Security Logging and Monitoring Failures
  - Security-relevant events (login, permission changes) are logged.
  - Logs do not contain PII or credentials.

A10 Server-Side Request Forgery (SSRF)
  - User-supplied URLs are validated against an allowlist before fetch.

After the checklist, emit a FINDINGS section:
- Format: `[SEVERITY] OWASP-A0X file:line — description — remediation`
- SEVERITY: CRITICAL | HIGH | MEDIUM | LOW
- Order: CRITICAL first.
- If no findings: "Security review passed. No findings."
```

## Expected inputs

- `<TARGET>` — file path, directory path, or raw `git diff` output.
- `<DEPTH>` — optional review depth: `"quick"` (highest-risk items only), `"standard"` (full OWASP Top 10), `"deep"` (includes supply-chain and design issues).

## Expected outputs

- A completed OWASP Top 10 checklist with PASS / FAIL / N/A per item.
- A `FINDINGS` section with severity-tagged, line-referenced bullets and remediation guidance.
- Items ordered CRITICAL → HIGH → MEDIUM → LOW.

## Worked example

**Scenario**: Review a new `login.py` endpoint before shipping.

**Invocation**:
```
/security-checklist TARGET=./api/login.py DEPTH=standard
```

**Expected output excerpt**:
```
A01 Broken Access Control      PASS  — route guarded by @require_login decorator.
A02 Cryptographic Failures     FAIL  — JWT secret read from a hard-coded string on line 8.
A03 Injection                  PASS  — SQLAlchemy ORM used throughout; no raw queries.
A07 Auth Failures              FAIL  — password compared with == instead of hmac.compare_digest.
…

FINDINGS:
- [CRITICAL] A02 login.py:8  — JWT_SECRET hard-coded as "mysecret"; move to environment variable.
- [HIGH]     A07 login.py:34 — Timing-safe comparison not used for password check; use hmac.compare_digest.
```
