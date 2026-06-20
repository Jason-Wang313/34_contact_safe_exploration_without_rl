# Submission Version Log

## v3 - 2026-06-15

- Wrote `docs/full_scale_execution_plan.md` before substantive v3 edits.
- Added `scripts/run_full_scale_contact_safe_suite.py`, a RAM-light standard-library full-scale experiment runner.
- Ran a 10-family, 12-regime, 14-policy, 96-seed suite representing 123,863,040 candidate contact-probe decisions.
- Generated `results/full_scale/seed_metrics.csv`, `aggregate_metrics.csv`, `experiment_summary.json`, `representative_trace.csv`, table snippets, and validation notes.
- Generated vector figures under `figures/full_scale/`.
- Rewrote `main.tex` as a 25-page v3 final full-scale manuscript with adaptive certificates, safety filters, oracle gaps, negative controls, hardware protocols, deployment checklists, and extended appendices.
- Built the canonical PDF at `C:/Users/wangz/Downloads/34.pdf` and removed local `main.pdf`.
- Verified final PDF page count, hash, text markers, build logs, and visual rendering.

## v4 Visual Hardening - 2026-06-20

- Added the VLA role-model `hyperref` box policy to `main.tex`.
- Rebuilt the canonical Downloads PDF.
- Verified 25 pages, size 346,308 bytes, SHA256 `1209B26370B1118689B8D53DFC6BCDC9B1A278E00C8B9877289D58A3C289E232`, and no local `main.pdf`.
- Verified one-point red internal link boxes on pages 4, 5, 6, and 7, with no cyan boxes. The manuscript has no cite/url link annotations, so green cite/url boxes are configured but not present.

## v2 - 2026-06-13

- Added discontinuous-contact stress generation to `scripts/recover_paper34.py`.
- Generated `docs/contact_discontinuity_stress.csv`.
- Generated `docs/contact_discontinuity_stress_table.tex`.
- Updated the manuscript with a visible v2 hardening note, discontinuity stress table, narrowed abstract, and stronger limitations.
- Added `scripts/build_pdf.ps1` to build from `main.tex`, copy to Downloads, and remove local `main.pdf`.
- Removed stale Desktop-copy language from the audit status.

## v1 - 2026-06-11

- Recovered initial contact-safe-exploration paper package with literature sweep, deterministic toy benchmark, ICLR-style manuscript, final audit, canonical Downloads PDF, Desktop-copy status, and public GitHub repo.
