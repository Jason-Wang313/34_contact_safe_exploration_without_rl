# Experiment Rigor Checklist

- [x] Main simulator is `scripts/recover_paper34.py`.
- [x] Main run uses 2,000 deterministic seeds.
- [x] Baselines include random force, conservative probing, and certificate expansion.
- [x] Main metrics include covered cells, violations, and return.
- [x] V2 stress attacks the local smoothness certificate with discontinuous low-limit pockets.
- [x] Negative boundary is explicit: under harm-5 scoring on discontinuous fields, conservative probing beats certificate expansion.
- [ ] No hardware validation.
- [ ] No high-fidelity contact simulator.
- [ ] No learned or calibrated contact-limit model.
- [ ] No CBF, safe RL, or MPC safety-filter baseline implementation.

Decision: mechanism evidence only; terminal state is workshop-only / strong-revise.
