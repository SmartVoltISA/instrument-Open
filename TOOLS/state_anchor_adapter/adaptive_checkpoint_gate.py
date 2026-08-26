#!/usr/bin/env python3
"""Portable adaptive checkpoint decision gate."""
from __future__ import annotations
from dataclasses import asdict
from typing import Any
from continuity_risk_detector import from_state
from state_anchor_adapter import AnchorPolicy, HardwareProfile, policy, should_checkpoint

def evaluate(profile: HardwareProfile, state: dict[str, Any], *, risk='normal', steps_since_anchor=0, event=None, verification_age_steps=0, prior_risk_score=None):
    continuity = from_state(state, steps_since_anchor=steps_since_anchor, verification_age_steps=verification_age_steps, prior_risk_score=prior_risk_score)
    effective_risk = risk
    if continuity.level == 'CRITICAL' or continuity.immediate_checkpoint:
        effective_risk = 'critical'
    elif continuity.level == 'ELEVATED' and effective_risk in {'low','normal'}:
        effective_risk = 'high'
    hp = policy(profile, risk=effective_risk, steps_since_anchor=steps_since_anchor)
    target = min(hp.target_steps, continuity.recommended_target_steps)
    combined = AnchorPolicy(target_steps=max(1,target), maximum_steps=hp.maximum_steps, pressure=hp.pressure, reason=hp.reason + [f'continuity risk = {continuity.level}'] + continuity.reasons)
    due, reason = should_checkpoint(steps_since_anchor=steps_since_anchor, policy_value=combined, event=event)
    if continuity.immediate_checkpoint:
        due, reason = True, 'continuity risk requires immediate checkpoint'
    return {'checkpoint_due': due, 'reason': reason, 'policy': asdict(combined), 'continuity': asdict(continuity), 'effective_risk': effective_risk}
