# Novelty Decision

## Chosen Thesis

Contact-safe exploration can be framed as certified safe frontier growth before reward-policy learning. The robot asks which touch is certified safe to try next, not which exploratory action has the highest learned reward.

## Why This Survives The Hostile Prior Set

- Safe RL is relevant but centers learned policies and constrained exploration.
- CBFs and safety filters are relevant but often assume the safety model rather than studying how a contact safe set is discovered.
- Tactile exploration is relevant but often optimizes information or classification rather than harm-aware frontier permission.
- Contact-rich manipulation is relevant but does not always isolate safe exploration before task execution.

## Novel Contribution Shape

1. A contact-specific certificate frontier over candidate probes.
2. A full-scale synthetic suite spanning 10 families, 12 regimes, 14 policies, and 123,863,040 represented decisions.
3. Evidence that fixed certificates are brittle, adaptive and MPC-style filters are stronger, and overconfident certificates are unsafe.
4. A reviewer-facing boundary that separates synthetic mechanism evidence from hardware validation.

## Risk Assessment

The result is paper-worthy as a synthetic mechanism study, but the hardware claim remains unproven. A deployment paper must measure force/tactile limits, stop latency, anisotropy, friction, deformation memory, discontinuities, and operator override behavior.

## V3 Boundary

Proceed as a final full-scale synthetic mechanism paper. Do not claim universal safety, hardware transfer, or a deployable oracle. Claim that contact exploration should use inspectable, calibrated certificates when unsafe contact has real cost.
