import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from continuity_risk_detector import ContinuityMetrics, assess

def test_normal():
    r=assess(ContinuityMetrics())
    assert r.level=='NORMAL' and r.recommended_target_steps==5 and not r.immediate_checkpoint

def test_contradiction_forces_checkpoint():
    r=assess(ContinuityMetrics(contradiction_count=1))
    assert r.immediate_checkpoint and r.recommended_target_steps==1

def test_maximum_forces_checkpoint():
    r=assess(ContinuityMetrics(steps_since_anchor=10))
    assert r.immediate_checkpoint and r.recommended_target_steps==1

def test_incomplete_state_forces_checkpoint():
    r=assess(ContinuityMetrics(state_completeness=.49))
    assert r.immediate_checkpoint
