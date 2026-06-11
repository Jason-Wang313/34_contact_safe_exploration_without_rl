# Hostile Prior Work

1. Safe reinforcement learning already studies exploration under constraints, but usually frames safety as a learned policy or value constraint.
2. Control barrier functions certify safety, but often assume a model rather than contact-limit discovery through probing.
3. Tactile exploration work probes unknown objects, but often optimizes information gain rather than safe set expansion.
4. Contact-rich manipulation plans through contact, but does not always isolate exploration as a certificate-growing process.

The defensible novelty is therefore not safety, exploration, or contact individually. It is the interface: guarded contact probes that expand a certified safe set without RL.
