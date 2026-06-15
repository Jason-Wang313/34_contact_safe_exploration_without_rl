# Experiment Rigor Checklist

- [x] Legacy simulator is `scripts/recover_paper34.py`.
- [x] Legacy v2 discontinuity stress remains available in `docs/contact_discontinuity_stress.csv`.
- [x] Full-scale runner is `scripts/run_full_scale_contact_safe_suite.py`.
- [x] Full-scale suite covers 10 contact-field families.
- [x] Full-scale suite covers 12 operating regimes.
- [x] Full-scale suite covers 14 policies/baselines.
- [x] Full-scale suite uses 96 deterministic seeds.
- [x] Full-scale suite represents 123,863,040 candidate contact-probe decisions.
- [x] Baselines include random force, conservative probing, fixed/adaptive certificates, Lipschitz-safe expansion, interval reachability, CBF-style filtering, MPC-style filtering, safe active-learning UCB, tactile-gradient probing, discontinuity detection, oracle limits, and overconfident negative control.
- [x] Stress controls include smooth nominal contact, discontinuities, sparse high-harm hazards, sensor noise, sensor bias, delayed stop, anisotropy, friction shift, deformable memory, high frontier value, high harm, and free-safe control.
- [x] Metrics include coverage, frontier coverage, information gain, violations, severity, high-harm violations, false-safe expansion, false blocking, utility, harm-weighted utility, blocked rate, regret to oracle, and win rate.
- [x] Negative control is explicit: overconfident certificates incur 98.66 violations per seed.
- [x] Oracle upper bound is reported: 417.8 utility and zero violations.
- [x] Generated tables and figures are manuscript-ready under `results/full_scale/` and `figures/full_scale/`.
- [ ] No hardware validation.
- [ ] No high-fidelity contact physics simulator.
- [ ] No learned contact-limit model trained on real tactile/force logs.

Decision: final full-scale synthetic mechanism evidence; hardware validation remains the next layer.
