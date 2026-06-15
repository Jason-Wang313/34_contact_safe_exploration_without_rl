# Submission Attack Log

Updated: 2026-06-15

## Attack Rounds

1. Closest-prior attack: safe RL, CBFs, tactile exploration, MPC safety filters, and safe active learning already cover safety-aware exploration. Response: keep novelty to contact-limit certificate growth before reward-policy learning.
2. Evidence attack: the benchmark is synthetic. Response: make the paper a final full-scale synthetic mechanism study and state the hardware boundary clearly.
3. Certificate attack: the margin is hand-designed and assumes local smoothness. Response: add adaptive margins, Lipschitz, interval, CBF-style, MPC-style, UCB, discontinuity, oracle, and overconfident variants.
4. Harm-scaling attack: coverage can look good even if unsafe contacts are costly. Response: report violation severity, high-harm events, harm-weighted utility, and overconfident negative controls.
5. Artifact attack: v1 kept `main.pdf` locally and recorded stale Desktop-copy status. Response: build script copies only to Downloads and removes local PDF.
6. Scope attack: the short v2 note could not support a final claim. Response: expand to a 25-page manuscript with 123,863,040 represented decisions, figures, tables, stress controls, hardware protocols, and reviewer-facing appendices.

## V3 Outcome

The paper is now final under the full-scale synthetic-mechanism standard. MPC-style filtering reaches 341.2 utility; adaptive certificates reach 289.6; fixed certificates remain brittle; overconfident certificates expose the danger of unsafe margins. The supported claim is calibrated contact-safe frontier growth, not a universal safety guarantee.
