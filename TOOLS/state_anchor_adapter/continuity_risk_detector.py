#!/usr/bin/env python3
"""Portable Continuity Risk Detector v0.1.

Scores only explicit, user-supplied process/state signals. It does not inspect
model internals or claim to measure model context or memory capacity.
"""
from __future__ import annotations
import argparse, json
from dataclasses import asdict, dataclass
from typing import Any

@dataclass
class ContinuityMetrics:
    steps_since_anchor: int = 0
    unresolved_count: int = 0
    unknown_count: int = 0
    contradiction_count: int = 0
    error_count: int = 0
    branch_count: int = 0
    decision_count: int = 0
    state_size_ratio: float = 1.0
    state_completeness: float = 1.0
    verification_age_steps: int = 0
    recent_state_change: float = 0.0
    prior_risk_score: float | None = None

@dataclass
class ContinuityAssessment:
    score: float
    level: str
    recommended_target_steps: int
    immediate_checkpoint: bool
    reasons: list[str]
    metrics: dict[str, Any]

LEVELS = ((0.00, 'NORMAL'), (0.30, 'WATCH'), (0.55, 'ELEVATED'), (0.75, 'CRITICAL'))

def _clamp(v: float) -> float:
    return max(0.0, min(1.0, float(v)))

def assess(m: ContinuityMetrics) -> ContinuityAssessment:
    reasons=[]; parts=[]
    parts.append(_clamp(m.steps_since_anchor/10)*.25)
    if m.steps_since_anchor >= 5: reasons.append('checkpoint distance is at or beyond target')
    parts += [_clamp(m.unresolved_count/5)*.10, _clamp(m.unknown_count/5)*.10]
    if m.unresolved_count or m.unknown_count: reasons.append('unresolved or unknown state is accumulating')
    parts += [_clamp(m.contradiction_count/2)*.15, _clamp(m.error_count/2)*.10]
    if m.contradiction_count: reasons.append('contradiction detected')
    if m.error_count: reasons.append('recent error state detected')
    parts += [_clamp(m.branch_count/3)*.08, _clamp(m.decision_count/3)*.04]
    if m.branch_count: reasons.append('state has branched')
    if m.decision_count: reasons.append('decision history is growing')
    parts += [_clamp((m.state_size_ratio-1)/4)*.04,
              (1-_clamp(m.state_completeness))*.07,
              _clamp(m.verification_age_steps/10)*.05,
              _clamp(m.recent_state_change)*.02]
    if m.state_completeness < .8: reasons.append('state completeness is degraded')
    if m.verification_age_steps >= 5: reasons.append('last verification is old')
    score=_clamp(sum(parts))
    if m.prior_risk_score is not None: score=_clamp(score*.85+_clamp(m.prior_risk_score)*.15)
    level='NORMAL'
    for threshold,name in LEVELS:
        if score >= threshold: level=name
    target=1 if level=='CRITICAL' or m.contradiction_count or m.error_count else 2 if level=='ELEVATED' else 3 if level=='WATCH' else 5
    immediate=(level=='CRITICAL' or bool(m.contradiction_count) or bool(m.error_count)
               or m.steps_since_anchor>=10 or m.state_completeness<.5)
    if immediate: reasons.append('immediate checkpoint condition')
    return ContinuityAssessment(round(score,4),level,min(10,max(1,target)),immediate,list(dict.fromkeys(reasons)),asdict(m))

def from_state(state: dict[str,Any], *, steps_since_anchor=0, verification_age_steps=0, prior_risk_score=None):
    return assess(ContinuityMetrics(
        steps_since_anchor=steps_since_anchor,
        unresolved_count=len(state.get('unresolved',[]) or []),
        unknown_count=len(state.get('unknown',[]) or []),
        contradiction_count=int(state.get('contradiction_count',0) or 0),
        error_count=int(state.get('error_count',0) or 0),
        branch_count=int(state.get('branch_count',0) or 0),
        decision_count=int(state.get('decision_count',0) or 0),
        state_size_ratio=float(state.get('state_size_ratio',1.0) or 1.0),
        state_completeness=float(state.get('state_completeness',1.0) or 1.0),
        verification_age_steps=verification_age_steps,
        recent_state_change=float(state.get('recent_state_change',0.0) or 0.0),
        prior_risk_score=prior_risk_score))

def main():
    p=argparse.ArgumentParser(description='Portable Continuity Risk Detector')
    p.add_argument('--state',required=True); p.add_argument('--steps',type=int,default=0)
    p.add_argument('--verification-age',type=int,default=0); p.add_argument('--prior-score',type=float,default=None)
    a=p.parse_args(); print(json.dumps(asdict(from_state(json.loads(a.state),steps_since_anchor=a.steps,verification_age_steps=a.verification_age,prior_risk_score=a.prior_score)),ensure_ascii=False,indent=2))

if __name__=='__main__': main()
