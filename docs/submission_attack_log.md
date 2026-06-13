# Submission Attack Log

Updated: 2026-06-13

## Attack Rounds

1. Closest-prior attack: safe RL, control barrier functions, tactile exploration, and safe active learning already cover safety-aware exploration. Response: keep novelty to contact-limit certificate growth without reward-policy learning.
2. Evidence attack: the benchmark is a synthetic contact field. Response: mark the paper workshop-only / strong-revise.
3. Certificate attack: the margin is hand-written and assumes local smoothness. Response: add v2 discontinuous-contact stress.
4. Harm-scaling attack: coverage can look good even if unsafe contacts are costly. Response: report harm-5 utility where conservative probing beats the certificate under discontinuities.
5. Artifact attack: v1 kept `main.pdf` locally and recorded stale Desktop-copy status. Response: build script copies only to Downloads and removes local PDF.

## V2 Outcome

The paper remains workshop-only / strong-revise. The smooth-field result supports certificate expansion as a mechanism, but the discontinuity stress narrows the claim: certificate expansion needs calibrated local smoothness and unsafe-contact harm. Under harm-5 scoring on discontinuous fields, conservative probing scores 22.726 while certificate expansion scores 22.356.
