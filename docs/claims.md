# Claims

## Supported Claims

- Contact exploration should treat probe safety as the primary state variable, not as a penalty learned after unsafe actions.
- Certificate-guided safe frontier growth can cover more useful contact cells than conservative low-force probing while causing far fewer violations than random force exploration.
- Fixed-margin certificates are useful but brittle when contact-limit smoothness, sensing, stop latency, or harm assumptions fail.
- Adaptive margins, interval/reachability reasoning, MPC-style filtering, safe active learning, and discontinuity detection are stronger than a single fixed margin.
- Overconfident certificates are dangerous: high coverage is not safety.
- The v3 full-scale suite supports these claims across 123,863,040 represented candidate probe decisions.

## Claims That Still Need Hardware Evidence

- The exact numerical utilities will transfer to a particular robot, tool, object, or tactile sensor.
- Measured hardware contact limits will match the synthetic family structure.
- A real robot can estimate local smoothness, stop latency, anisotropy, friction, and harm well enough for deployment.
- Human operators will accept the explanation and override protocol without additional interface studies.

## Claims To Avoid Or Qualify

- Do not claim safe RL, CBFs, or tactile exploration ignore safety.
- Do not claim certificates are universal safety guarantees.
- Do not claim the oracle limit map is deployable.
- Do not claim synthetic utility values are real damage probabilities.
- Do not claim a fixed margin is sufficient for hardware.

## Evidence Base

- Legacy v2 stress: brittle low-limit pockets can make conservative probing beat fixed certificate expansion under high harm.
- V3 full-scale suite: 10 families, 12 regimes, 14 policies, 96 seeds, 192 cells, 4 candidate probes per cell, and 123,863,040 represented decisions.
- V3 baselines: random force, low-force probing, fixed/adaptive certificates, Lipschitz and interval filters, CBF-style and MPC-style filters, safe active learning, tactile gradients, discontinuity detection, oracle maps, and overconfident negative control.
