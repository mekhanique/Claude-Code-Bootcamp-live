# Architecture — module-08/before/pricing.py

## Data Flow

```
caller
  │
  │  items: list[tuple], country: str, customer: dict|None
  ▼
┌─────────────────────────────────────────────────────┐
│                      calc()                         │
│                                                     │
│  ┌──────────────┐    subtotal                       │
│  │  Item loop   │ ──────────┐                       │
│  │  + discount  │           │                       │
│  └──────────────┘           ▼                       │
│                    ┌─────────────────┐              │
│                    │   Tax lookup    │── tax ──┐    │
│                    │  (if/elif chain)│         │    │
│                    └─────────────────┘         │    │
│                    ┌─────────────────┐         │    │
│                    │ Shipping tiers  │─ ship ──┤    │
│                    │  (<50/200/free) │         │    │
│                    └─────────────────┘         │    │
│                                                ▼    │
│                              round(subtotal+tax+ship,2)
└─────────────────────────────────────────────────────┘
  │
  │  float (final price, 2 dp)
  ▼
caller
```

## Components

**Item loop + discount** (`calc`, lines 10–29)
Iterates `items`, skipping `None` entries and tuples that are not length-3 or have non-positive qty/price. Applies a 10 % VIP discount first; if the customer is not VIP, applies a coupon discount (SAVE10 = 10 %, SAVE20 = 20 %). Accumulates a running subtotal `t`.

**Tax lookup** (`calc`, lines 39–48)
Maps `country` to a flat tax rate via an `if/elif` chain (US 7 %, GB/FR 20 %, DE 19 %, default 10 %). Multiplies the subtotal to produce `tax`.

**Shipping tiers** (`calc`, lines 50–56)
Three flat tiers on the pre-tax subtotal: < 50 → $9.99, 50–199 → $4.99, ≥ 200 → free.

**Public interface** — `calc(items, country, customer) -> float`
Single entry point. Returns the rounded final price. No I/O, no side effects.

## Known Limitations

1. Discount logic is not composable — a VIP customer with a coupon silently loses the coupon benefit; there is no way to stack discounts.
2. Tax rates are hard-coded; adding a new country requires a code change.
3. Shipping tiers are also hard-coded; no way to inject custom rates (e.g. express shipping).
4. Invalid item tuples (wrong length, bad qty/price) are silently skipped with no warning to the caller.
5. `customer` is an untyped dict; there is no validation — a misspelled key (`"VIP"` instead of `"vip"`) fails silently.
