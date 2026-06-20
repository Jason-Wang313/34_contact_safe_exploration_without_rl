# Paper34 Full-Scale Execution Plan

## Current Claim

Paper34 argues that contact exploration can be organized around certified safe
set expansion instead of reinforcement-learning exploration. The v2 manuscript
has a useful mechanism boundary: certificate expansion outperforms random force
probing and conservative probing on smooth contact fields, but brittle
low-limit discontinuities can make conservative probing preferable under high
harm weighting. The v3 paper should keep that boundary while greatly expanding
the evidence across contact-field families, safety assumptions, sensing noise,
candidate force schedules, discontinuity detectors, formal safety filters, and
negative controls.

## Gaps To Close

1. The current manuscript is only a short mechanism note.
2. The current simulator has one smooth field family, one discontinuous stress,
and three policies.
3. The certificate is a hand-written local smoothness margin rather than a
family of calibrated safety filters.
4. There are no CBF-style, MPC safety-filter, interval reachability,
Lipschitz-safe, safe active-learning, tactile-gradient, or oracle baselines.
5. There are no sensor noise, drift, anisotropy, friction, delayed stop,
deformability, high-harm, or false-safe controls.
6. The docs incorrectly describe a final Downloads PDF even though
`C:/Users/wangz/Downloads/34.pdf` is absent.
7. The final v3 paper must reach at least 25 pages through real technical
content, not padding.

## Target Full-Scale Experiment

Create `scripts/run_full_scale_contact_safe_suite.py` using only the Python
standard library. Write outputs to `results/full_scale/` and figures to
`figures/full_scale/`. Use RAM-light sequential execution: stream seed-level
rows to disk, keep only compact aggregate accumulators in memory, and save one
representative trace that shows smooth expansion, a discontinuity failure,
sensor-noise recovery, and an overconfident certificate violation.

Target scale:

- 10 contact-field families
- 12 operating regimes
- 14 policies / baselines
- 96 deterministic seeds
- 192 contact cells per seed
- 4 candidate probe levels considered per contact cell
- 123,863,040 represented candidate contact-probe decisions

## Contact-Field Families

1. `smooth_elastic_surface`: locally smooth contact limits with mild curvature.
2. `brittle_low_limit_pockets`: rare unsafe discontinuities inside otherwise
smooth fields.
3. `anisotropic_brush_contact`: directional safe forces differ by probe axis.
4. `friction_cliff_surface`: tangential friction changes sharply across cells.
5. `thin_shell_contact`: high value frontier with low force tolerance.
6. `foam_deformation_contact`: safe limits drift after repeated probing.
7. `cable_snag_field`: sparse cells have high snag harm under lateral probes.
8. `peg_in_hole_edge_contact`: useful information lies near narrow unsafe
edges.
9. `soft_tissue_proxy`: low-force probing is usually safe but high harm when
violated.
10. `calibration_control_surface`: wide safe margin where aggressive methods
should be competitive.

## Operating Regimes

1. `smooth_nominal`: smooth limits and calibrated sensors.
2. `dense_discontinuities`: frequent brittle low-limit pockets.
3. `sparse_catastrophic_hazards`: rare cells with high violation harm.
4. `force_sensor_noise`: noisy measured force limits.
5. `sensor_bias_drift`: systematic force-limit bias over the episode.
6. `delayed_stop`: probes overshoot after a violation is detected.
7. `anisotropic_limits`: safe limits depend on probe direction.
8. `friction_shift`: normal force is safe but tangential slip is not.
9. `deformable_memory`: previous probes change later safe limits.
10. `frontier_value_high`: coverage near the unknown frontier is valuable.
11. `high_harm_weight`: unsafe contacts dominate the utility metric.
12. `free_safe_control`: violations are impossible, so aggressive exploration
should often win.

## Policies / Baselines

1. `random_force`: samples cell and probe force aggressively.
2. `uniform_low_force`: conservative low-force probing everywhere.
3. `frontier_low_force`: expands spatially but always uses the low probe.
4. `fixed_margin_certificate`: v2-style local margin certificate.
5. `adaptive_margin_certificate`: increases margin after surprise violations
and relaxes after stable regions.
6. `lipschitz_safe_expansion`: uses a calibrated local Lipschitz bound.
7. `interval_reachability_filter`: carries lower/upper safe-limit intervals.
8. `cbf_style_safety_filter`: filters candidate probes through a barrier-like
margin condition.
9. `mpc_safety_filter`: evaluates short-horizon coverage against violation
risk.
10. `safe_active_learning_ucb`: explores uncertain cells only when an upper
confidence bound remains safe.
11. `tactile_gradient_probe`: follows local gradients in measured limits.
12. `discontinuity_detector`: pauses expansion after abrupt residual changes.
13. `oracle_limit_map`: knows true local limits and supplies an upper bound.
14. `overconfident_certificate`: negative control with an unsafe margin.

## Metrics

For each seed-level row record:

- covered cells
- frontier coverage
- useful information gain
- total violations
- violation severity
- high-harm violations
- false-safe expansions
- false-blocked safe probes
- cumulative utility
- harm-weighted utility
- probe count
- abstention / blocked-probe rate
- regret to oracle
- win indicator
- family, regime, method, seed, cell count, and candidate probes

For aggregates record means, standard errors, win rates, oracle gaps,
violation reductions, frontier-coverage gains, high-harm miss rates, and
sensitivity to harm weighting.

## Ablations And Stress Tests

1. Smoothness sweep from locally Lipschitz to brittle discontinuous fields.
2. Harm-weight sweep from low-cost scratches to catastrophic contact.
3. Sensor-noise and sensor-bias sweeps.
4. Probe-force grid size and candidate-force schedule ablations.
5. Delayed-stop overshoot control.
6. Anisotropic normal/tangential contact limits.
7. Deformable memory where earlier probing changes later limits.
8. Free-safe-control regime where aggressive exploration should win.
9. Overconfident-certificate negative control.
10. Oracle-limit-map upper bound.

## Figures And Tables

Generate manuscript-ready artifacts:

- `full_scale_scale.tex`: families, regimes, policies, seeds, cells, candidate
probes, and represented decisions.
- `full_scale_main_performance.tex`: main policy comparison.
- `full_scale_regime_winners.tex`: regime-level winner table.
- `full_scale_family_summary.tex`: family-level coverage, violations, utility,
and oracle gap.
- `full_scale_stress_controls.tex`: discontinuity, noise, high-harm,
free-safe, and overconfidence controls.
- `coverage_by_method.pdf`: coverage and utility by policy.
- `violation_tradeoff.pdf`: coverage versus violation severity.
- `regime_winner_phase.pdf`: winner map across operating regimes.
- `representative_trace.csv`: explicit trace for smooth expansion,
discontinuity failure, sensor-noise recovery, and overconfident violation.

## Manuscript Expansion Strategy

Rewrite `main.tex` into a v3 final full-scale manuscript:

1. Keep the v2 boundary: certificates help only when local safety assumptions
are calibrated.
2. Add the v3 marker and 123,863,040-decision scale.
3. Expand related work around safe RL, control barrier functions, MPC safety
filters, safe active learning, tactile exploration, contact-rich
manipulation, reachability, and formal safety certificates.
4. Formalize contact-safe exploration as safe frontier growth with candidate
probe filtering, harm-aware utility, local limit uncertainty, and abstention.
5. Report full-scale results, discontinuity controls, high-harm controls,
free-safe controls, sensor-noise controls, overconfident negative controls,
and oracle-limit gaps.
6. Add appendices for contact families, regimes, policies, metrics,
calibration, hardware measurement, reviewer attacks, falsification criteria,
limitations, reproducibility, and deployment checklists.

The final rendered PDF must be at least 25 pages. Extra length must come from
real content: broader experiments, ablations, detailed interpretations,
failure cases, hardware protocols, and reproducibility.

## RAM-Light Execution Strategy

- Simulate one seed/method/family/regime at a time.
- Stream seed-level rows directly to CSV.
- Store only aggregate accumulators and one representative trace in memory.
- Generate compact vector PDF figures directly with standard-library code.
- Avoid storing per-candidate tensors or full contact fields for all seeds.
- Keep intermediate PDFs local and ignored.
- Do not copy to Downloads until the final 25+ page manuscript passes
verification.

## Final Acceptance Checklist

Paper34 is not final until all of the following are true:

- `docs/full_scale_execution_plan.md` exists before substantive edits.
- Full-scale runner completes reproducibly.
- Generated outputs exist in `results/full_scale/`.
- Generated figures exist in `figures/full_scale/`.
- Manuscript renders to at least 25 pages.
- PDF text contains `v3 final full-scale` and `123,863,040`.
- Build log has no fatal LaTeX errors, unresolved references, undefined
citations, or overfull boxes.
- Final Downloads PDF is copied only to `C:/Users/wangz/Downloads/34.pdf`.
- Local `main.pdf` is removed after final build.
- Docs and status files describe v3, not stale v2 readiness.

## Execution Outcome

The plan was executed on 2026-06-15. The final suite completed with 10
contact-field families, 12 regimes, 14 policies, 96 deterministic seeds, 192
cells, 4 candidate probes per cell, and 123,863,040 represented candidate
contact-probe decisions. The final manuscript rendered to 25 pages, was copied
only to `C:/Users/wangz/Downloads/34.pdf`, and left no local `main.pdf`.
On 2026-06-20, the final PDF was rebuilt with the VLA role-model hyperref box
policy. The rebuilt artifact has SHA256
`1209B26370B1118689B8D53DFC6BCDC9B1A278E00C8B9877289D58A3C289E232` and
VLA-style one-point red internal link boxes on pages 4, 5, 6, and 7.
