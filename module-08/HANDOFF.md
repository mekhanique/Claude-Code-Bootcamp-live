# Refactor Handoff — module-08/before/pricing.py

## What changed
- Extracted per-item validation and discount logic into private `_item_subtotal`; replaced 7-level nested `if/else` with early returns.
- Replaced the `if/elif` tax chain with a `_TAX_RATES` dict lookup (default `0.10` via `.get`).
- Flattened nested shipping tiers into a single `if/elif/else`; renamed `t` → `subtotal`, `ship` → `shipping`.

## Why
Pure readability refactor for Module 08. No behaviour change intended or made. The original nesting depth (7 levels) made discount precedence and skip conditions hard to audit at a glance.

## Risk + how to roll back
**Risk:** Low. `calc` signature and all return values are unchanged; the test suite pins byte-identical output.

**Roll back:** `git checkout HEAD -- module-08/before/pricing.py`

## Watch-outs for the next engineer
- `_item_subtotal` is private by convention (`_` prefix) — do not add it to any public API surface without updating the signature constraint note in `constraints.md`.
- VIP discount takes priority over coupon: `_item_subtotal` returns early after the VIP branch, so a customer with both `vip: True` and a `coupon` key gets only the 10 % VIP discount. This matches the original behaviour — do not reorder the branches.
- `_COUPON_FACTORS.get(customer.get("coupon", ""), 1.0)` silently gives factor `1.0` for unknown coupons. If a new coupon is added, update `_COUPON_FACTORS` — there is no fallthrough warning.
- Tax rates for GB and FR are both `0.20`; this is intentional and correct. Do not "deduplicate" them into a shared key without verifying VAT rules.
