# jb-drf-billing

Reusable billing/subscriptions foundations for Django/DRF projects.

Pattern:
- abstract models in this package
- concrete models + migrations in integrator projects
- configuration via `JB_DRF_BILLING`

## Roadmap

- **Phase 1-2 (done):** core lib, abstract models, RevenueCat adapter, admin pattern.
- **Phase 3 (in progress):** mobile + RevenueCat real (trial configurable, mobile gating).
- **Phase 4:** Stripe adapter (web + Android checkout, customer portal, real webhook signature verification). See [`PHASE_4_TODO.md`](./PHASE_4_TODO.md) for the actionable checklist.

To find all in-code markers for Phase 4 work:
```bash
grep -r "TODO\[phase-4-stripe\]" .
```
