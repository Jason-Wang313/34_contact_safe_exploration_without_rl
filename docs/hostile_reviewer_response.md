# Hostile Reviewer Response

## Likely Rejection

This is still synthetic. Safe RL, CBFs, MPC safety filters, and tactile exploration already cover parts of safety-aware contact exploration. The suite uses stylized expected rollouts rather than hardware force logs.

## Honest Response

We agree that the paper is not a hardware validation. The contribution is a full-scale synthetic mechanism study: it isolates contact-safe frontier growth and shows why certificates must expose calibration, uncertainty, discontinuity, stop-latency, and harm assumptions.

The v3 evidence is much broader than the v2 note. It covers 10 families, 12 regimes, 14 policies, 96 seeds, and 123,863,040 represented candidate decisions. It includes random force, conservative probing, fixed/adaptive certificates, Lipschitz and interval filters, CBF-style and MPC-style filters, safe active learning, tactile gradients, discontinuity detection, oracle limits, and overconfident negative controls.

The claim is deliberately bounded. Fixed certificates are not presented as a final hardware safety system. The useful policies are the ones that make the certificate inspectable and calibrated; the overconfident negative control shows that certificate language can be unsafe when assumptions are hidden.

## Required Upgrade For Hardware Evidence

- Calibrate contact-limit smoothness, force sensing, stop latency, anisotropy, friction, and deformation on hardware.
- Add measured discontinuity detection and conservative fallback.
- Compare against real CBF, safe RL, MPC safety-filter, and tactile active-learning implementations.
- Report raw contact logs, high-harm events, operator overrides, and videos of representative successes and failures.
