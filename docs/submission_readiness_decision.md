# Submission Readiness Decision

Decision: final full-scale synthetic mechanism paper.

## Why This Is Now Final Under The Synthetic-Mechanism Standard

- The manuscript renders to 25 pages and includes the v3 final full-scale marker.
- The full-scale suite represents 123,863,040 candidate contact-probe decisions.
- The evidence includes broad baselines, ablations, stress controls, negative controls, oracle upper bounds, and reviewer-facing limitations.
- The key result is not padded by page count: MPC-style and adaptive safety filters improve utility while preserving the boundary that fixed certificates fail under discontinuity and overconfidence fails under harm.
- The canonical PDF exists only at `C:/Users/wangz/Downloads/34.pdf`; local `main.pdf` is removed after build.
- Final build logs have no fatal errors, unresolved references, undefined citations, overfull boxes, or TeX error lines.
- The delivered PDF was rendered and visually inspected, including VLA-style red internal link boxes on pages 4, 5, 6, and 7.

## Remaining Boundary

- This is not a hardware-validated robotics result.
- The synthetic contact limits, harm weights, and certificate assumptions must be replaced by measured force/tactile data for a hardware paper.
- The oracle limit map is only an upper bound.
- A real deployment needs measured stop latency, force bias, anisotropy, friction, deformation memory, and operator override logging.

## Next Work Beyond This Paper

- Measure contact-limit maps on real objects.
- Train and calibrate contact-limit and discontinuity estimators.
- Evaluate the same mechanism in high-fidelity contact simulation or hardware.
- Add human-supervisor override studies for risky contact probes.
