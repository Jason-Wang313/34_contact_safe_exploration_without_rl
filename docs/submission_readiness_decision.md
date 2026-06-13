# Submission Readiness Decision

Decision: workshop-only / strong-revise.

## Why Not Submit-Ready

- Evidence is a synthetic contact field.
- The certificate margin is hand-written.
- V2 shows the certificate is brittle under discontinuous low-limit pockets.
- There is no hardware validation or high-fidelity contact simulation.
- There is no comparison to CBF, safe RL, MPC safety filters, or tactile active-learning baselines.

## Why Not Kill

- The safe-frontier-growth framing is clear and useful.
- The smooth-field toy task cleanly separates random force, conservative probing, and certificate expansion.
- The v2 stress makes the discontinuity and harm-weight boundary explicit.
- The narrowed claim is useful as a mechanism note.

## Required Next Work

- Calibrate contact-limit smoothness and force sensing on real robot contacts.
- Add discontinuity detection and conservative fallback.
- Compare against established safe-control and safe-exploration baselines.
- Report multiple unsafe-contact harm regimes.
