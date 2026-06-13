# Hostile Reviewer Response

## Likely Rejection

This is a hand-written smoothness certificate in a toy contact field. Safe RL and barrier certificates already exist, and the method may become unsafe when contact limits are discontinuous.

## Honest Response

We agree. The contribution is not a full safe-exploration algorithm, a hardware result, or a universal safety guarantee. It is a mechanism note: for contact exploration, a robot can sometimes grow a certified safe frontier without learning a reward policy.

The v2 stress quantifies the boundary. In brittle discontinuous fields, certificate expansion covers 32.291 cells but incurs 3974 unsafe contacts. Under harm-5 scoring, conservative probing beats it, 22.726 to 22.356. The paper should claim calibrated certificate growth only.

## Required Upgrade For Main-Track Submission

- Calibrate contact-limit smoothness on hardware or high-fidelity simulation.
- Add discontinuity detection or fallback conservative probing.
- Compare against CBF, safe RL, model-predictive safety-filter, and tactile active-learning baselines.
- Report safety/coverage tradeoffs under multiple unsafe-contact harm weights.
