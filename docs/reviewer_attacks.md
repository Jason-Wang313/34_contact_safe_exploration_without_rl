# Reviewer Attacks

1. "This is just control barrier functions."
   - Response: CBFs are a core baseline family, but the paper centers contact-limit discovery and safe frontier growth when the contact model is not yet known.

2. "Safe RL can do this."
   - Response: the paper studies the pre-RL safety object: which candidate touch is certified safe before reward-policy learning is allowed to explore.

3. "The suite is synthetic."
   - Response: correct; the paper is explicitly a synthetic mechanism study and does not claim hardware validation.

4. "The certificate assumptions are hand-designed."
   - Response: yes; v3 attacks those assumptions with discontinuity, noise, bias, delayed-stop, anisotropy, friction, deformation, high-harm, free-safe, oracle, and overconfident controls.

5. "Neighbor-based certificates break at discontinuities."
   - Response: true, and that is one of the main results. Fixed certificates are weaker than adaptive, interval, MPC-style, and discontinuity-aware policies.

6. "Coverage is not safety."
   - Response: exactly. The paper reports violations, severity, high-harm violations, false-safe expansions, false blocking, utility, harm-weighted utility, and regret separately.

## Most Likely Weakness

The paper remains weakest at external validity. A main-track hardware version should measure real contact limits and show that the calibrated certificate predicts safe frontier growth on physical objects.
