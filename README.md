# Contact Safe Exploration Without RL

Paper 34 final v3 artifact for the robotics 60 batch.

- Thesis: robots can expand contact knowledge with certificates and guarded probes rather than reinforcement learning.
- Manuscript: `main.tex`
- Canonical PDF: `C:/Users/wangz/Downloads/34.pdf`
- Final PDF pages: 25
- Final PDF SHA256: `9243DFAC7F540DE2EED48E9FAFA89318B23030224572AE6912EC952EDCA19548`
- Build command: `powershell -ExecutionPolicy Bypass -File scripts/build_pdf.ps1`
- Full-scale runner: `python scripts/run_full_scale_contact_safe_suite.py`
- Full-scale outputs: `results/full_scale/`
- Figures: `figures/full_scale/`

## v3 Evidence

The v3 manuscript replaces the compact v2 mechanism note with a full-scale
synthetic suite covering 10 contact-field families, 12 regimes, 14 policies,
96 deterministic seeds, 192 contact cells, 4 candidate probes per cell, and
123,863,040 represented candidate contact-probe decisions.

Key aggregate results:

- Random force: 139.7 covered cells and 41.30 violations per seed.
- Uniform low force: 55.0 covered cells and 0.08 violations per seed.
- Fixed-margin certificate: 208.4 utility and 19.55 violations per seed.
- Adaptive-margin certificate: 289.6 utility and 3.61 violations per seed.
- MPC safety filter: 341.2 utility and 76.6 regret to oracle.
- Oracle limit map: 417.8 utility and zero violations.
- Overconfident certificate: 98.66 violations per seed and only 46.0 utility.

## Boundary

This is a final full-scale synthetic mechanism paper, not a hardware validation
paper. The supported claim is conditional: contact exploration should grow an
inspectable certified frontier when unsafe contact has real cost, and that
certificate must expose calibration, sensing, stop latency, discontinuity, and
harm assumptions.
