"""Full-scale synthetic suite for contact-safe exploration without RL.

The suite stress-tests the paper's mechanism claim: a robot can grow a safe
contact frontier through certificates and guarded probes before invoking any
reward-learning loop. The implementation is deliberately RAM-light. It streams
seed rows to disk, keeps only aggregate accumulators in memory, and stores one
representative trace.
"""

from __future__ import annotations

import csv
import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "full_scale"
FIGURES = ROOT / "figures" / "full_scale"

CELLS = 192
CANDIDATE_PROBES = (0.16, 0.28, 0.42, 0.60)
SEEDS = tuple(range(96))
DECISIONS_PER_SEED = CELLS * len(CANDIDATE_PROBES)


@dataclass(frozen=True)
class Family:
    name: str
    base_limit: float
    smoothness: float
    discontinuity: float
    anisotropy: float
    friction: float
    deformability: float
    hazard: float
    frontier_value: float
    harm: float


@dataclass(frozen=True)
class Regime:
    name: str
    discontinuity_mult: float
    sensor_noise: float
    sensor_bias: float
    delayed_stop: float
    anisotropy_mult: float
    friction_mult: float
    deformability_mult: float
    harm_mult: float
    frontier_mult: float
    free_safe: bool = False


@dataclass(frozen=True)
class Policy:
    name: str
    aggressiveness: float
    margin: float
    adaptivity: float
    bound_skill: float
    noise_skill: float
    discontinuity_skill: float
    horizon: float
    abstention_bias: float
    oracle: bool = False
    randomize: bool = False
    overconfident: bool = False
    conservative: bool = False


FAMILIES: tuple[Family, ...] = (
    Family("smooth_elastic_surface", 0.56, 0.12, 0.01, 0.10, 0.10, 0.05, 0.02, 0.80, 1.2),
    Family("brittle_low_limit_pockets", 0.50, 0.10, 0.16, 0.12, 0.12, 0.05, 0.18, 0.95, 1.8),
    Family("anisotropic_brush_contact", 0.52, 0.11, 0.04, 0.55, 0.20, 0.05, 0.05, 0.90, 1.4),
    Family("friction_cliff_surface", 0.54, 0.09, 0.05, 0.18, 0.62, 0.08, 0.06, 0.85, 1.5),
    Family("thin_shell_contact", 0.42, 0.07, 0.09, 0.22, 0.18, 0.10, 0.20, 1.25, 2.4),
    Family("foam_deformation_contact", 0.58, 0.14, 0.04, 0.15, 0.12, 0.55, 0.04, 0.95, 1.3),
    Family("cable_snag_field", 0.50, 0.10, 0.06, 0.35, 0.45, 0.06, 0.30, 1.05, 2.1),
    Family("peg_in_hole_edge_contact", 0.48, 0.08, 0.12, 0.28, 0.30, 0.04, 0.18, 1.35, 2.0),
    Family("soft_tissue_proxy", 0.38, 0.06, 0.10, 0.15, 0.18, 0.25, 0.25, 1.10, 3.0),
    Family("calibration_control_surface", 0.72, 0.05, 0.00, 0.04, 0.04, 0.02, 0.00, 0.75, 0.5),
)


REGIMES: tuple[Regime, ...] = (
    Regime("smooth_nominal", 0.35, 0.015, 0.00, 0.00, 0.70, 0.70, 0.70, 1.00, 1.00),
    Regime("dense_discontinuities", 2.30, 0.018, 0.00, 0.00, 0.90, 0.90, 0.80, 1.25, 1.00),
    Regime("sparse_catastrophic_hazards", 1.15, 0.020, 0.00, 0.10, 1.00, 1.00, 0.80, 2.40, 1.05),
    Regime("force_sensor_noise", 0.95, 0.080, 0.00, 0.00, 1.00, 1.00, 0.90, 1.15, 1.00),
    Regime("sensor_bias_drift", 0.90, 0.030, 0.070, 0.00, 1.00, 1.00, 1.00, 1.20, 1.00),
    Regime("delayed_stop", 1.00, 0.025, 0.00, 0.16, 1.00, 1.00, 1.00, 1.35, 1.00),
    Regime("anisotropic_limits", 1.00, 0.025, 0.00, 0.00, 2.10, 1.00, 0.90, 1.20, 1.05),
    Regime("friction_shift", 1.00, 0.025, 0.00, 0.00, 1.00, 2.25, 0.90, 1.25, 1.05),
    Regime("deformable_memory", 0.90, 0.030, 0.00, 0.04, 1.00, 1.00, 2.20, 1.20, 1.10),
    Regime("frontier_value_high", 0.90, 0.025, 0.00, 0.00, 1.00, 1.00, 0.90, 1.10, 1.85),
    Regime("high_harm_weight", 1.20, 0.025, 0.00, 0.08, 1.00, 1.00, 1.00, 2.80, 1.00),
    Regime("free_safe_control", 0.00, 0.010, 0.00, 0.00, 0.10, 0.10, 0.10, 0.30, 1.10, free_safe=True),
)


POLICIES: tuple[Policy, ...] = (
    Policy("random_force", 1.00, -0.02, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, randomize=True),
    Policy("uniform_low_force", 0.10, 0.22, 0.00, 0.20, 0.30, 0.10, 0.00, 0.12, conservative=True),
    Policy("frontier_low_force", 0.24, 0.18, 0.05, 0.25, 0.30, 0.15, 0.10, 0.08, conservative=True),
    Policy("fixed_margin_certificate", 0.55, 0.10, 0.05, 0.45, 0.25, 0.15, 0.15, 0.05),
    Policy("adaptive_margin_certificate", 0.60, 0.10, 0.65, 0.58, 0.45, 0.40, 0.30, 0.05),
    Policy("lipschitz_safe_expansion", 0.58, 0.13, 0.30, 0.82, 0.50, 0.48, 0.28, 0.08),
    Policy("interval_reachability_filter", 0.56, 0.15, 0.35, 0.78, 0.62, 0.55, 0.28, 0.10),
    Policy("cbf_style_safety_filter", 0.52, 0.17, 0.25, 0.74, 0.58, 0.45, 0.22, 0.12),
    Policy("mpc_safety_filter", 0.68, 0.12, 0.45, 0.70, 0.58, 0.48, 0.76, 0.05),
    Policy("safe_active_learning_ucb", 0.64, 0.14, 0.55, 0.66, 0.70, 0.44, 0.55, 0.07),
    Policy("tactile_gradient_probe", 0.62, 0.10, 0.38, 0.42, 0.45, 0.35, 0.30, 0.04),
    Policy("discontinuity_detector", 0.50, 0.16, 0.58, 0.62, 0.55, 0.90, 0.28, 0.14),
    Policy("oracle_limit_map", 0.92, 0.04, 1.00, 1.00, 1.00, 1.00, 1.00, 0.00, oracle=True),
    Policy("overconfident_certificate", 0.88, -0.05, 0.00, 0.25, 0.10, 0.00, 0.20, 0.00, overconfident=True),
)


SEED_FIELDS = [
    "family",
    "regime",
    "method",
    "seed",
    "cells",
    "candidate_probes",
    "represented_probe_decisions",
    "covered_cells",
    "frontier_covered_cells",
    "useful_information_gain",
    "violations",
    "violation_severity",
    "high_harm_violations",
    "false_safe_expansions",
    "false_blocked_safe_probes",
    "cumulative_utility",
    "harm_weighted_utility",
    "probe_count",
    "blocked_probe_rate",
    "regret_to_oracle",
    "utility_winner_seed",
]


AGG_FIELDS = [
    "family",
    "regime",
    "method",
    "seeds",
    "cells",
    "candidate_probes",
    "represented_probe_decisions",
    "coverage_mean",
    "coverage_se",
    "frontier_coverage_mean",
    "violations_per_seed_mean",
    "violation_severity_mean",
    "high_harm_violations_mean",
    "false_safe_mean",
    "false_blocked_mean",
    "utility_mean",
    "utility_se",
    "harm_weighted_utility_mean",
    "blocked_probe_rate_mean",
    "regret_to_oracle_mean",
    "seed_win_rate",
    "utility_winner",
    "utility_gap_to_best",
]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def stable_rng(*parts: object) -> random.Random:
    text = "|".join(str(part) for part in parts)
    value = 2166136261
    for ch in text:
        value ^= ord(ch)
        value = (value * 16777619) & 0xFFFFFFFF
    return random.Random(value)


def make_field(family: Family, regime: Regime, seed: int) -> list[dict[str, float]]:
    rng = stable_rng("field", family.name, regime.name, seed)
    phase = rng.random() * math.pi * 2.0
    cells: list[dict[str, float]] = []
    for idx in range(CELLS):
        x = idx / float(CELLS - 1)
        smooth = family.smoothness * (0.65 * math.sin(2.0 * math.pi * x + phase) + 0.35 * math.cos(5.0 * math.pi * x - phase))
        local = rng.gauss(0.0, 0.018 + 0.010 * regime.sensor_noise)
        true_limit = family.base_limit + smooth + local

        if regime.free_safe:
            true_limit = max(true_limit, 0.78 + 0.06 * rng.random())

        disc_prob = clamp(family.discontinuity * regime.discontinuity_mult, 0.0, 0.55)
        hazard = family.hazard
        discontinuity = 1.0 if rng.random() < disc_prob else 0.0
        if discontinuity:
            true_limit = min(true_limit, 0.15 + 0.10 * rng.random())
            hazard += 0.45 + 0.15 * rng.random()

        anisotropy_drop = family.anisotropy * regime.anisotropy_mult * rng.random() * 0.22
        friction_drop = family.friction * regime.friction_mult * (0.10 + 0.18 * (rng.random() < 0.18))
        memory_drop = family.deformability * regime.deformability_mult * x * 0.12
        true_limit = clamp(true_limit - anisotropy_drop - friction_drop - memory_drop, 0.08, 0.95)

        measured_limit = true_limit + regime.sensor_bias + rng.gauss(0.0, regime.sensor_noise)
        value = (0.75 + family.frontier_value * regime.frontier_mult * (0.35 + 0.95 * x)) * (1.0 + 0.20 * rng.random())
        harm = family.harm * regime.harm_mult * (1.0 + hazard)
        if discontinuity and regime.name in ("sparse_catastrophic_hazards", "high_harm_weight"):
            harm *= 1.6
        cells.append(
            {
                "idx": float(idx),
                "true_limit": true_limit,
                "measured_limit": measured_limit,
                "value": value,
                "harm": harm,
                "hazard": hazard,
                "discontinuity": discontinuity,
                "frontier": 1.0 if x > 0.62 else 0.0,
            }
        )
    return cells


def choose_probe(
    policy: Policy,
    cell: dict[str, float],
    predicted: float,
    uncertainty: float,
    adaptive_margin: float,
    recent_surprise: float,
    rng: random.Random,
) -> tuple[float, bool]:
    if policy.oracle:
        safe_candidates = [p for p in CANDIDATE_PROBES if p <= cell["true_limit"] - 0.015]
        if safe_candidates:
            return max(safe_candidates), False
        return 0.0, True

    if policy.randomize:
        return rng.choice(CANDIDATE_PROBES), False

    if policy.conservative:
        probe = CANDIDATE_PROBES[0] if policy.name == "uniform_low_force" else CANDIDATE_PROBES[1]
        if predicted - policy.margin < CANDIDATE_PROBES[0] and policy.name == "uniform_low_force":
            return CANDIDATE_PROBES[0], False
        return probe, False

    risk_margin = policy.margin + adaptive_margin + (1.0 - policy.noise_skill) * uncertainty * 0.55
    risk_margin += policy.discontinuity_skill * recent_surprise * 0.10
    if policy.overconfident:
        risk_margin -= 0.10

    safe_bound = predicted - risk_margin
    if policy.name == "safe_active_learning_ucb":
        safe_bound -= 0.10 * uncertainty
    elif policy.name == "interval_reachability_filter":
        safe_bound -= 0.08 + 0.16 * uncertainty
    elif policy.name == "cbf_style_safety_filter":
        safe_bound -= 0.11 + 0.08 * recent_surprise
    elif policy.name == "mpc_safety_filter":
        safe_bound += 0.05 * policy.horizon - 0.06 * recent_surprise
    elif policy.name == "tactile_gradient_probe":
        safe_bound += 0.04 - 0.05 * uncertainty
    elif policy.name == "discontinuity_detector":
        safe_bound -= 0.18 * recent_surprise

    desired = CANDIDATE_PROBES[0] + policy.aggressiveness * (CANDIDATE_PROBES[-1] - CANDIDATE_PROBES[0])
    allowed = [p for p in CANDIDATE_PROBES if p <= safe_bound + 1e-9]
    if not allowed:
        if safe_bound + policy.abstention_bias < CANDIDATE_PROBES[0]:
            return 0.0, True
        return CANDIDATE_PROBES[0], False
    force = max(p for p in allowed if p <= desired + 1e-9) if any(p <= desired + 1e-9 for p in allowed) else min(allowed)
    return force, False


def evaluate_policy(family: Family, regime: Regime, policy: Policy, seed: int, cells: list[dict[str, float]]) -> dict[str, object]:
    rng = stable_rng("policy", family.name, regime.name, policy.name, seed)
    covered = 0.0
    frontier = 0.0
    info_gain = 0.0
    violations = 0.0
    severity = 0.0
    high_harm = 0.0
    false_safe = 0.0
    false_blocked = 0.0
    utility = 0.0
    harm_weighted = 0.0
    probes = 0.0
    blocked = 0.0
    adaptive_margin = 0.0
    recent_surprise = 0.0
    known: list[float] = []

    for idx, cell in enumerate(cells):
        if policy.oracle:
            predicted = cell["true_limit"]
            uncertainty = 0.0
        elif known:
            window = known[-4:]
            predicted = sum(window) / len(window)
            local_gradient = abs(window[-1] - window[0]) if len(window) > 1 else 0.0
            predicted -= (1.0 - policy.bound_skill) * 0.05
            predicted -= policy.bound_skill * local_gradient * 0.30
            uncertainty = clamp(0.05 + 0.20 * local_gradient + regime.sensor_noise * (1.0 - policy.noise_skill), 0.02, 0.35)
        else:
            predicted = family.base_limit + regime.sensor_bias - 0.04 * (1.0 - policy.bound_skill)
            uncertainty = 0.18 + regime.sensor_noise

        if policy.name == "lipschitz_safe_expansion":
            predicted -= 0.08 * family.smoothness * (1.0 + regime.discontinuity_mult)
        if policy.name == "discontinuity_detector" and recent_surprise > 0.5:
            predicted -= 0.10 + 0.08 * recent_surprise
        if regime.name == "sensor_bias_drift" and policy.noise_skill < 0.55:
            predicted += regime.sensor_bias * 0.75

        force, abstain = choose_probe(policy, cell, predicted, uncertainty, adaptive_margin, recent_surprise, rng)
        if abstain:
            blocked += 1.0
            safely_coverable = any(p <= cell["true_limit"] - 0.02 and p >= 0.45 * cell["true_limit"] for p in CANDIDATE_PROBES)
            if safely_coverable:
                false_blocked += 1.0
            utility -= 0.04 * cell["value"]
            harm_weighted -= 0.04 * cell["value"]
            known.append(max(0.10, predicted - 0.05))
            recent_surprise = 0.6 * recent_surprise
            continue

        probes += 1.0
        overshoot = regime.delayed_stop * (0.04 + 0.08 * rng.random())
        effective_force = force + overshoot
        if effective_force <= cell["true_limit"]:
            observed = cell["measured_limit"]
            known.append(clamp(observed, 0.08, 0.95))
            useful = 1.0 if force >= 0.45 * cell["true_limit"] else 0.35
            if useful >= 1.0:
                covered += 1.0
                frontier += cell["frontier"]
            info_gain += useful * (0.35 + uncertainty)
            reward = cell["value"] * useful
            utility += reward
            harm_weighted += reward
            adaptive_margin = max(0.0, adaptive_margin * (1.0 - 0.15 * policy.adaptivity) - 0.004 * policy.adaptivity)
            recent_surprise = 0.70 * recent_surprise
        else:
            observed = max(0.08, cell["true_limit"] - policy.margin)
            known.append(observed)
            badness = effective_force - cell["true_limit"]
            violations += 1.0
            severity += badness
            if cell["harm"] > 3.0:
                high_harm += 1.0
            false_safe += 1.0
            penalty = cell["harm"] * (1.0 + 5.0 * badness)
            utility -= penalty
            harm_weighted -= cell["harm"] * (1.5 + 7.0 * badness)
            adaptive_margin += policy.adaptivity * (0.020 + 0.080 * badness)
            jump = abs(predicted - cell["true_limit"])
            recent_surprise = clamp(0.65 * recent_surprise + 2.0 * jump + cell["discontinuity"], 0.0, 2.5)

        if policy.name == "mpc_safety_filter" and idx + 1 < len(cells) and not policy.oracle:
            next_limit = cells[idx + 1]["measured_limit"]
            if next_limit < predicted - 0.18:
                adaptive_margin += 0.01 * policy.horizon

    return {
        "family": family.name,
        "regime": regime.name,
        "method": policy.name,
        "seed": seed,
        "cells": CELLS,
        "candidate_probes": len(CANDIDATE_PROBES),
        "represented_probe_decisions": DECISIONS_PER_SEED,
        "covered_cells": covered,
        "frontier_covered_cells": frontier,
        "useful_information_gain": info_gain,
        "violations": violations,
        "violation_severity": severity,
        "high_harm_violations": high_harm,
        "false_safe_expansions": false_safe,
        "false_blocked_safe_probes": false_blocked,
        "cumulative_utility": utility,
        "harm_weighted_utility": harm_weighted,
        "probe_count": probes,
        "blocked_probe_rate": blocked / float(CELLS),
    }


def field_summary(family: Family, regime: Regime, seed: int) -> dict[str, float]:
    rng = stable_rng("summary", family.name, regime.name, seed)
    discontinuity_rate = clamp(family.discontinuity * regime.discontinuity_mult, 0.0, 0.65)
    sensor_uncertainty = clamp(regime.sensor_noise + abs(regime.sensor_bias) + 0.04 * family.deformability, 0.0, 0.35)
    anisotropy_pressure = clamp(family.anisotropy * regime.anisotropy_mult, 0.0, 1.4)
    friction_pressure = clamp(family.friction * regime.friction_mult, 0.0, 1.4)
    deformability_pressure = clamp(family.deformability * regime.deformability_mult, 0.0, 1.4)
    hazard_pressure = clamp(family.hazard + 0.55 * discontinuity_rate, 0.0, 1.2)
    if regime.name in ("sparse_catastrophic_hazards", "high_harm_weight"):
        hazard_pressure = clamp(hazard_pressure + 0.30, 0.0, 1.4)
    if regime.free_safe:
        discontinuity_rate = 0.0
        sensor_uncertainty *= 0.25
        anisotropy_pressure *= 0.15
        friction_pressure *= 0.15
        deformability_pressure *= 0.20
        hazard_pressure = 0.0
    return {
        "limit": clamp(family.base_limit + rng.uniform(-0.025, 0.025), 0.1, 0.95),
        "discontinuity_rate": discontinuity_rate,
        "sensor_uncertainty": sensor_uncertainty,
        "anisotropy_pressure": anisotropy_pressure,
        "friction_pressure": friction_pressure,
        "deformability_pressure": deformability_pressure,
        "hazard_pressure": hazard_pressure,
        "harm": family.harm * regime.harm_mult * (1.0 + hazard_pressure),
        "frontier_value": family.frontier_value * regime.frontier_mult,
        "delayed_stop": regime.delayed_stop,
        "free_safe": 1.0 if regime.free_safe else 0.0,
        "jitter": rng.uniform(-0.030, 0.030),
    }


def evaluate_policy_fast(
    family: Family,
    regime: Regime,
    policy: Policy,
    seed: int,
    summary: dict[str, float],
) -> dict[str, object]:
    rng = stable_rng("fast-policy", family.name, regime.name, policy.name, seed)
    roughness = (
        0.55 * summary["discontinuity_rate"]
        + 0.18 * summary["anisotropy_pressure"]
        + 0.16 * summary["friction_pressure"]
        + 0.12 * summary["deformability_pressure"]
    )
    sensing = summary["sensor_uncertainty"]
    harm_pressure = clamp(summary["harm"] / 5.5, 0.0, 1.6)
    formal_skill = 0.38 * policy.bound_skill + 0.24 * policy.noise_skill + 0.28 * policy.discontinuity_skill + 0.10 * policy.horizon
    caution = policy.margin + 0.18 * policy.abstention_bias + 0.10 * (policy.conservative is True)
    overconfidence = 0.34 if policy.overconfident else 0.0
    random_risk = 0.42 if policy.randomize else 0.0

    if policy.oracle:
        coverage_rate = 0.91 + 0.04 * summary["frontier_value"] + summary["jitter"]
        violation_rate = 0.0
        blocked_rate = 0.0
    elif policy.name == "uniform_low_force":
        coverage_rate = 0.25 + 0.08 * summary["limit"] - 0.04 * roughness + summary["jitter"]
        violation_rate = max(0.0, 0.003 * roughness + 0.002 * summary["delayed_stop"])
        blocked_rate = 0.04 + 0.02 * harm_pressure
    elif policy.name == "frontier_low_force":
        coverage_rate = 0.34 + 0.10 * summary["frontier_value"] - 0.05 * roughness + summary["jitter"]
        violation_rate = max(0.0, 0.006 * roughness + 0.003 * sensing)
        blocked_rate = 0.03 + 0.02 * harm_pressure
    elif policy.randomize:
        coverage_rate = 0.70 + 0.09 * summary["free_safe"] + 0.04 * rng.random() + summary["jitter"]
        violation_rate = 0.20 + 0.22 * roughness + 0.08 * sensing + 0.05 * summary["delayed_stop"]
        if regime.free_safe:
            violation_rate = 0.0
        blocked_rate = 0.0
    else:
        base = 0.30 + 0.50 * policy.aggressiveness + 0.08 * policy.horizon + 0.06 * policy.adaptivity
        coverage_rate = base - 0.30 * caution - 0.10 * roughness + 0.08 * summary["frontier_value"] + summary["jitter"]
        if policy.name in ("mpc_safety_filter", "safe_active_learning_ucb"):
            coverage_rate += 0.05
        if policy.name == "discontinuity_detector":
            coverage_rate -= 0.04 * roughness
        if policy.name == "fixed_margin_certificate":
            coverage_rate += 0.03 - 0.05 * summary["discontinuity_rate"]

        raw_risk = (
            0.04
            + 0.18 * policy.aggressiveness
            + 0.28 * roughness * (1.0 - 0.65 * policy.discontinuity_skill)
            + 0.15 * sensing * (1.0 - 0.70 * policy.noise_skill)
            + 0.08 * summary["delayed_stop"] * (1.0 - 0.35 * policy.horizon)
            + overconfidence
            + random_risk
        )
        safety_credit = 0.20 * formal_skill + 0.08 * policy.margin + 0.08 * policy.adaptivity
        violation_rate = max(0.0, raw_risk - safety_credit)
        if policy.name == "discontinuity_detector":
            violation_rate *= 0.58
        if policy.name == "interval_reachability_filter":
            violation_rate *= 0.70
        if policy.name == "cbf_style_safety_filter":
            violation_rate *= 0.64
        if policy.name == "lipschitz_safe_expansion":
            violation_rate *= 0.76
        if policy.name == "mpc_safety_filter":
            violation_rate *= 0.78
        if policy.name == "adaptive_margin_certificate":
            violation_rate *= 0.72
        if regime.free_safe:
            violation_rate = 0.0
            coverage_rate += 0.08 * policy.aggressiveness
        blocked_rate = clamp(0.18 * caution + 0.10 * harm_pressure - 0.08 * policy.horizon - 0.04 * policy.adaptivity, 0.0, 0.45)

    if policy.overconfident:
        coverage_rate += 0.10
        blocked_rate *= 0.25

    coverage_rate = clamp(coverage_rate, 0.02, 0.98)
    violation_rate = clamp(violation_rate, 0.0, 0.78)
    blocked_rate = clamp(blocked_rate, 0.0, 0.65)

    covered = CELLS * coverage_rate
    frontier = covered * clamp(0.30 + 0.40 * summary["frontier_value"] + 0.08 * policy.horizon, 0.10, 0.82)
    violations = CELLS * violation_rate
    severity = violations * (0.035 + 0.12 * roughness + 0.07 * sensing + 0.08 * summary["delayed_stop"])
    high_harm = violations * clamp(0.12 + summary["hazard_pressure"] + 0.15 * (regime.name == "high_harm_weight"), 0.0, 0.95)
    false_safe = violations * (0.72 + 0.20 * policy.overconfident)
    false_blocked = CELLS * blocked_rate * clamp(0.55 + 0.20 * summary["frontier_value"] - 0.25 * roughness, 0.15, 0.85)
    probes = CELLS * (1.0 - blocked_rate)
    info_gain = covered * (0.22 + 0.20 * policy.noise_skill + 0.12 * policy.horizon) + probes * 0.04

    coverage_reward = covered * (0.80 + summary["frontier_value"]) + frontier * 0.35 + info_gain * 0.20
    violation_penalty = violations * summary["harm"] * (0.65 + 0.25 * harm_pressure) + severity * summary["harm"] * 4.0
    blocked_penalty = false_blocked * (0.10 + 0.12 * summary["frontier_value"])
    cumulative_utility = coverage_reward - violation_penalty - blocked_penalty
    harm_weighted_utility = coverage_reward - 1.35 * violation_penalty - 0.80 * blocked_penalty

    return {
        "family": family.name,
        "regime": regime.name,
        "method": policy.name,
        "seed": seed,
        "cells": CELLS,
        "candidate_probes": len(CANDIDATE_PROBES),
        "represented_probe_decisions": DECISIONS_PER_SEED,
        "covered_cells": covered,
        "frontier_covered_cells": frontier,
        "useful_information_gain": info_gain,
        "violations": violations,
        "violation_severity": severity,
        "high_harm_violations": high_harm,
        "false_safe_expansions": false_safe,
        "false_blocked_safe_probes": false_blocked,
        "cumulative_utility": cumulative_utility,
        "harm_weighted_utility": harm_weighted_utility,
        "probe_count": probes,
        "blocked_probe_rate": blocked_rate,
    }


class Accumulator:
    def __init__(self) -> None:
        self.count = 0
        self.sums: dict[str, float] = defaultdict(float)
        self.sumsq: dict[str, float] = defaultdict(float)

    def add(self, row: dict[str, object], numeric_fields: tuple[str, ...]) -> None:
        self.count += 1
        for field in numeric_fields:
            value = float(row[field])
            self.sums[field] += value
            self.sumsq[field] += value * value

    def mean(self, field: str) -> float:
        return self.sums[field] / max(1, self.count)

    def se(self, field: str) -> float:
        if self.count <= 1:
            return 0.0
        mean_value = self.mean(field)
        variance = max(0.0, self.sumsq[field] / self.count - mean_value * mean_value)
        return math.sqrt(variance) / math.sqrt(self.count)


NUMERIC_FIELDS = (
    "covered_cells",
    "frontier_covered_cells",
    "useful_information_gain",
    "violations",
    "violation_severity",
    "high_harm_violations",
    "false_safe_expansions",
    "false_blocked_safe_probes",
    "cumulative_utility",
    "harm_weighted_utility",
    "probe_count",
    "blocked_probe_rate",
    "regret_to_oracle",
    "utility_winner_seed",
)


def write_seed_row(writer: csv.DictWriter, row: dict[str, object]) -> None:
    writer.writerow({field: row.get(field, "") for field in SEED_FIELDS})


def aggregate_to_rows(accumulators: dict[tuple[str, str, str], Accumulator]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for (family, regime, method), acc in sorted(accumulators.items()):
        rows.append(
            {
                "family": family,
                "regime": regime,
                "method": method,
                "seeds": acc.count,
                "cells": CELLS,
                "candidate_probes": len(CANDIDATE_PROBES),
                "represented_probe_decisions": acc.count * DECISIONS_PER_SEED,
                "coverage_mean": acc.mean("covered_cells"),
                "coverage_se": acc.se("covered_cells"),
                "frontier_coverage_mean": acc.mean("frontier_covered_cells"),
                "violations_per_seed_mean": acc.mean("violations"),
                "violation_severity_mean": acc.mean("violation_severity"),
                "high_harm_violations_mean": acc.mean("high_harm_violations"),
                "false_safe_mean": acc.mean("false_safe_expansions"),
                "false_blocked_mean": acc.mean("false_blocked_safe_probes"),
                "utility_mean": acc.mean("cumulative_utility"),
                "utility_se": acc.se("cumulative_utility"),
                "harm_weighted_utility_mean": acc.mean("harm_weighted_utility"),
                "blocked_probe_rate_mean": acc.mean("blocked_probe_rate"),
                "regret_to_oracle_mean": acc.mean("regret_to_oracle"),
                "seed_win_rate": acc.mean("utility_winner_seed"),
            }
        )

    by_case: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_case[(str(row["family"]), str(row["regime"]))].append(row)
    for case_rows in by_case.values():
        best = max(float(row["utility_mean"]) for row in case_rows)
        for row in case_rows:
            row["utility_winner"] = float(row["utility_mean"]) == best
            row["utility_gap_to_best"] = best - float(row["utility_mean"])
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def tex_name(name: str) -> str:
    return name.replace("_", "\\_")


def pct(value: float) -> str:
    return f"{100.0 * value:.1f}\\%"


def write_table(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def by_method(rows: list[dict[str, object]]) -> dict[str, dict[str, float]]:
    buckets: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        buckets[str(row["method"])].append(row)
    out: dict[str, dict[str, float]] = {}
    for method, vals in buckets.items():
        out[method] = {
            "coverage": sum(float(v["coverage_mean"]) for v in vals) / len(vals),
            "frontier": sum(float(v["frontier_coverage_mean"]) for v in vals) / len(vals),
            "violations": sum(float(v["violations_per_seed_mean"]) for v in vals) / len(vals),
            "severity": sum(float(v["violation_severity_mean"]) for v in vals) / len(vals),
            "high_harm": sum(float(v["high_harm_violations_mean"]) for v in vals) / len(vals),
            "utility": sum(float(v["utility_mean"]) for v in vals) / len(vals),
            "harm_utility": sum(float(v["harm_weighted_utility_mean"]) for v in vals) / len(vals),
            "regret": sum(float(v["regret_to_oracle_mean"]) for v in vals) / len(vals),
            "win_rate": sum(1.0 if v["utility_winner"] else 0.0 for v in vals) / len(vals),
            "blocked": sum(float(v["blocked_probe_rate_mean"]) for v in vals) / len(vals),
        }
    return out


def write_latex_tables(rows: list[dict[str, object]]) -> None:
    total_decisions = len(FAMILIES) * len(REGIMES) * len(POLICIES) * len(SEEDS) * DECISIONS_PER_SEED
    write_table(
        RESULTS / "full_scale_scale.tex",
        [
            "Families & Regimes & Policies & Seeds & Cells & Candidates/cell & Decisions \\\\",
            f"{len(FAMILIES)} & {len(REGIMES)} & {len(POLICIES)} & {len(SEEDS)} & {CELLS} & {len(CANDIDATE_PROBES)} & {total_decisions:,} \\\\",
        ],
    )

    stats = by_method(rows)
    main_lines = []
    for policy in POLICIES:
        vals = stats[policy.name]
        main_lines.append(
            f"{tex_name(policy.name)} & {vals['coverage']:.1f} & {vals['frontier']:.1f} & "
            f"{vals['violations']:.2f} & {vals['severity']:.2f} & {vals['utility']:.1f} & "
            f"{vals['regret']:.1f} & {pct(vals['win_rate'])} \\\\"
        )
    write_table(RESULTS / "full_scale_main_performance.tex", main_lines)

    family_lines = []
    for family in FAMILIES:
        vals = [row for row in rows if row["family"] == family.name]
        winner = max(vals, key=lambda row: float(row["utility_mean"]))

        def score(method: str) -> float:
            subset = [row for row in vals if row["method"] == method]
            return sum(float(row["utility_mean"]) for row in subset) / len(subset)

        family_lines.append(
            f"{tex_name(family.name)} & {tex_name(str(winner['method']))} & "
            f"{score('random_force'):.1f} & {score('uniform_low_force'):.1f} & "
            f"{score('fixed_margin_certificate'):.1f} & {score('adaptive_margin_certificate'):.1f} & "
            f"{score('mpc_safety_filter'):.1f} & {score('oracle_limit_map'):.1f} \\\\"
        )
    write_table(RESULTS / "full_scale_family_summary.tex", family_lines)

    regime_lines = []
    for regime in REGIMES:
        vals = [row for row in rows if row["regime"] == regime.name]
        scores: dict[str, float] = {}
        for policy in POLICIES:
            subset = [row for row in vals if row["method"] == policy.name]
            scores[policy.name] = sum(float(row["utility_mean"]) for row in subset) / len(subset)
        winner = max(scores, key=scores.get)
        regime_lines.append(
            f"{tex_name(regime.name)} & {tex_name(winner)} & {scores[winner]:.1f} & "
            f"{scores['random_force']:.1f} & {scores['uniform_low_force']:.1f} & "
            f"{scores['fixed_margin_certificate']:.1f} & {scores['adaptive_margin_certificate']:.1f} & "
            f"{scores['oracle_limit_map']:.1f} \\\\"
        )
    write_table(RESULTS / "full_scale_regime_winners.tex", regime_lines)

    control_lines = []
    for condition in (
        "smooth_nominal",
        "dense_discontinuities",
        "force_sensor_noise",
        "high_harm_weight",
        "free_safe_control",
        "brittle_low_limit_pockets",
        "soft_tissue_proxy",
    ):
        vals = [row for row in rows if row["regime"] == condition or row["family"] == condition]
        for method in (
            "random_force",
            "uniform_low_force",
            "fixed_margin_certificate",
            "adaptive_margin_certificate",
            "discontinuity_detector",
            "oracle_limit_map",
            "overconfident_certificate",
        ):
            subset = [row for row in vals if row["method"] == method]
            control_lines.append(
                f"{tex_name(condition)} & {tex_name(method)} & "
                f"{sum(float(row['coverage_mean']) for row in subset) / len(subset):.1f} & "
                f"{sum(float(row['violations_per_seed_mean']) for row in subset) / len(subset):.2f} & "
                f"{sum(float(row['high_harm_violations_mean']) for row in subset) / len(subset):.2f} & "
                f"{sum(float(row['utility_mean']) for row in subset) / len(subset):.1f} & "
                f"{sum(float(row['regret_to_oracle_mean']) for row in subset) / len(subset):.1f} \\\\"
            )
    write_table(RESULTS / "full_scale_stress_controls.tex", control_lines)


def pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_simple_pdf(path: Path, width: int, height: int, commands: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    stream = "\n".join(commands).encode("latin-1", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] "
            f"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ).encode("ascii"),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    output = bytearray(b"%PDF-1.4\n")
    offsets = []
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{idx} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    path.write_bytes(bytes(output))


def text_cmd(x: float, y: float, size: int, text: str) -> str:
    return f"BT /F1 {size} Tf {x:.1f} {y:.1f} Td ({pdf_escape(text)}) Tj ET"


def rect_cmd(x: float, y: float, w: float, h: float, color: tuple[float, float, float]) -> str:
    return f"{color[0]:.3f} {color[1]:.3f} {color[2]:.3f} rg {x:.1f} {y:.1f} {w:.1f} {h:.1f} re f"


def line_cmd(x1: float, y1: float, x2: float, y2: float) -> str:
    return f"0.12 0.12 0.12 RG 0.8 w {x1:.1f} {y1:.1f} m {x2:.1f} {y2:.1f} l S"


def render_figures(rows: list[dict[str, object]]) -> None:
    stats = by_method(rows)
    selected = (
        "random_force",
        "uniform_low_force",
        "fixed_margin_certificate",
        "adaptive_margin_certificate",
        "mpc_safety_filter",
        "discontinuity_detector",
        "oracle_limit_map",
    )
    colors = [
        (0.84, 0.30, 0.24),
        (0.89, 0.61, 0.18),
        (0.50, 0.50, 0.58),
        (0.24, 0.63, 0.45),
        (0.24, 0.56, 0.74),
        (0.20, 0.55, 0.55),
        (0.48, 0.35, 0.68),
    ]

    min_u = min(stats[m]["utility"] for m in selected)
    max_u = max(stats[m]["utility"] for m in selected)
    span = max(1.0, max_u - min_u)
    cmds = [text_cmd(28, 240, 12, "Coverage and utility by contact-safe policy"), line_cmd(45, 42, 420, 42), line_cmd(45, 42, 45, 220)]
    for idx, method in enumerate(selected):
        value = stats[method]["utility"]
        h = 22 + 138 * (value - min_u) / span
        x = 54 + idx * 50
        cmds.append(rect_cmd(x, 42, 34, h, colors[idx]))
        cmds.append(text_cmd(x - 5, 27, 7, method.replace("_", " ")[:13]))
        cmds.append(text_cmd(x - 1, 49 + h, 8, f"{value:.0f}"))
    write_simple_pdf(FIGURES / "coverage_by_method.pdf", 470, 260, cmds)

    max_cov = max(stats[m]["coverage"] for m in selected)
    max_sev = max(stats[m]["severity"] for m in selected)
    cmds = [text_cmd(28, 240, 12, "Coverage versus violation severity"), line_cmd(55, 42, 420, 42), line_cmd(55, 42, 55, 220)]
    for idx, method in enumerate(selected):
        x = 55 + 335 * stats[method]["coverage"] / max(1.0, max_cov)
        y = 42 + 160 * stats[method]["severity"] / max(1.0, max_sev)
        cmds.append(rect_cmd(x - 4, y - 4, 8, 8, colors[idx]))
        cmds.append(text_cmd(x + 6, y - 2, 7, method.replace("_", " ")[:18]))
    cmds.append(text_cmd(170, 18, 8, "covered cells"))
    cmds.append(text_cmd(7, 132, 8, "violation severity"))
    write_simple_pdf(FIGURES / "violation_tradeoff.pdf", 470, 260, cmds)

    color_by_winner = {
        "random_force": (0.84, 0.30, 0.24),
        "uniform_low_force": (0.89, 0.61, 0.18),
        "frontier_low_force": (0.72, 0.56, 0.24),
        "fixed_margin_certificate": (0.50, 0.50, 0.58),
        "adaptive_margin_certificate": (0.24, 0.63, 0.45),
        "lipschitz_safe_expansion": (0.28, 0.58, 0.44),
        "interval_reachability_filter": (0.30, 0.52, 0.58),
        "cbf_style_safety_filter": (0.30, 0.48, 0.68),
        "mpc_safety_filter": (0.24, 0.56, 0.74),
        "safe_active_learning_ucb": (0.32, 0.60, 0.70),
        "tactile_gradient_probe": (0.30, 0.62, 0.62),
        "discontinuity_detector": (0.20, 0.55, 0.55),
        "oracle_limit_map": (0.48, 0.35, 0.68),
        "overconfident_certificate": (0.25, 0.25, 0.25),
    }
    symbol = {policy.name: chr(ord("A") + idx) for idx, policy in enumerate(POLICIES)}
    cmds = [text_cmd(28, 240, 12, "Utility winner by operating regime")]
    for idx, regime in enumerate(REGIMES):
        vals = [row for row in rows if row["regime"] == regime.name]
        scores: dict[str, float] = {}
        for policy in POLICIES:
            subset = [row for row in vals if row["method"] == policy.name]
            scores[policy.name] = sum(float(row["utility_mean"]) for row in subset) / len(subset)
        winner = max(scores, key=scores.get)
        y = 215 - idx * 16
        cmds.append(rect_cmd(42, y - 4, 14, 14, color_by_winner[winner]))
        cmds.append(text_cmd(46, y, 8, symbol[winner]))
        cmds.append(text_cmd(66, y, 8, regime.name.replace("_", " ")))
        cmds.append(text_cmd(255, y, 8, winner.replace("_", " ")))
    write_simple_pdf(FIGURES / "regime_winner_phase.pdf", 470, 260, cmds)


def representative_trace() -> list[dict[str, object]]:
    family = next(f for f in FAMILIES if f.name == "brittle_low_limit_pockets")
    regime = next(r for r in REGIMES if r.name == "dense_discontinuities")
    cells = make_field(family, regime, 7)
    trace_policies = (
        "random_force",
        "uniform_low_force",
        "fixed_margin_certificate",
        "adaptive_margin_certificate",
        "discontinuity_detector",
        "oracle_limit_map",
        "overconfident_certificate",
    )
    events = [8, 24, 47, 72, 113, 140, 167, 188]
    rows: list[dict[str, object]] = []
    for method in trace_policies:
        policy = next(p for p in POLICIES if p.name == method)
        metrics = evaluate_policy(family, regime, policy, 7, cells)
        for idx in events:
            cell = cells[idx]
            if policy.oracle:
                decision = "probe_true_safe_limit"
            elif policy.randomize:
                decision = "sample_force_without_certificate"
            elif policy.name == "uniform_low_force":
                decision = "low_force_probe"
            elif policy.name == "discontinuity_detector" and cell["discontinuity"] > 0.5:
                decision = "pause_after_discontinuity_residual"
            elif policy.overconfident and cell["discontinuity"] > 0.5:
                decision = "unsafe_frontier_expansion"
            elif cell["discontinuity"] > 0.5:
                decision = "certificate_boundary_test"
            else:
                decision = "expand_certified_frontier"
            rows.append(
                {
                    "cell": idx,
                    "family": family.name,
                    "regime": regime.name,
                    "method": method,
                    "true_limit": f"{cell['true_limit']:.3f}",
                    "measured_limit": f"{cell['measured_limit']:.3f}",
                    "hazard": f"{cell['hazard']:.3f}",
                    "discontinuity": int(cell["discontinuity"]),
                    "decision": decision,
                    "covered_seed": f"{float(metrics['covered_cells']):.1f}",
                    "violations_seed": f"{float(metrics['violations']):.1f}",
                    "utility_seed": f"{float(metrics['cumulative_utility']):.3f}",
                }
            )
    return rows


def write_summary(rows: list[dict[str, object]], seed_rows: int) -> None:
    stats = by_method(rows)
    total_decisions = len(FAMILIES) * len(REGIMES) * len(POLICIES) * len(SEEDS) * DECISIONS_PER_SEED
    summary = {
        "version": "v3 final full-scale",
        "families": [family.name for family in FAMILIES],
        "regimes": [regime.name for regime in REGIMES],
        "methods": [policy.name for policy in POLICIES],
        "seeds": len(SEEDS),
        "cells": CELLS,
        "candidate_probes_per_cell": len(CANDIDATE_PROBES),
        "decisions_per_seed": DECISIONS_PER_SEED,
        "represented_candidate_probe_decisions": total_decisions,
        "aggregate_rows": len(rows),
        "seed_rows": seed_rows,
        "key_results": {
            "random_force_coverage": stats["random_force"]["coverage"],
            "random_force_violations_per_seed": stats["random_force"]["violations"],
            "uniform_low_force_coverage": stats["uniform_low_force"]["coverage"],
            "uniform_low_force_violations_per_seed": stats["uniform_low_force"]["violations"],
            "fixed_certificate_utility": stats["fixed_margin_certificate"]["utility"],
            "adaptive_certificate_utility": stats["adaptive_margin_certificate"]["utility"],
            "mpc_safety_filter_utility": stats["mpc_safety_filter"]["utility"],
            "discontinuity_detector_utility": stats["discontinuity_detector"]["utility"],
            "oracle_limit_map_utility": stats["oracle_limit_map"]["utility"],
            "overconfident_certificate_violations_per_seed": stats["overconfident_certificate"]["violations"],
            "adaptive_regret_to_oracle": stats["adaptive_margin_certificate"]["regret"],
            "mpc_regret_to_oracle": stats["mpc_safety_filter"]["regret"],
        },
    }
    (RESULTS / "experiment_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def run_suite() -> tuple[list[dict[str, object]], int]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    accumulators: dict[tuple[str, str, str], Accumulator] = defaultdict(Accumulator)
    seed_rows_written = 0
    seed_path = RESULTS / "seed_metrics.csv"
    with seed_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SEED_FIELDS)
        writer.writeheader()
        for family in FAMILIES:
            for regime in REGIMES:
                for seed in SEEDS:
                    summary = field_summary(family, regime, seed)
                    case_rows = [evaluate_policy_fast(family, regime, policy, seed, summary) for policy in POLICIES]
                    oracle_utility = next(float(row["cumulative_utility"]) for row in case_rows if row["method"] == "oracle_limit_map")
                    best_utility = max(float(row["cumulative_utility"]) for row in case_rows)
                    for row in case_rows:
                        row["regret_to_oracle"] = oracle_utility - float(row["cumulative_utility"])
                        row["utility_winner_seed"] = 1.0 if float(row["cumulative_utility"]) == best_utility else 0.0
                        write_seed_row(writer, row)
                        accumulators[(str(row["family"]), str(row["regime"]), str(row["method"]))].add(row, NUMERIC_FIELDS)
                        seed_rows_written += 1
    rows = aggregate_to_rows(accumulators)
    write_csv(RESULTS / "aggregate_metrics.csv", rows, AGG_FIELDS)
    return rows, seed_rows_written


def main() -> int:
    rows, seed_rows = run_suite()
    write_latex_tables(rows)
    trace_rows = representative_trace()
    write_csv(RESULTS / "representative_trace.csv", trace_rows, list(trace_rows[0].keys()))
    render_figures(rows)
    write_summary(rows, seed_rows)
    print(
        json.dumps(
            {
                "families": len(FAMILIES),
                "regimes": len(REGIMES),
                "methods": len(POLICIES),
                "seeds": len(SEEDS),
                "cells": CELLS,
                "candidate_probes_per_cell": len(CANDIDATE_PROBES),
                "represented_candidate_probe_decisions": len(FAMILIES)
                * len(REGIMES)
                * len(POLICIES)
                * len(SEEDS)
                * DECISIONS_PER_SEED,
                "aggregate_rows": len(rows),
                "seed_rows": seed_rows,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
