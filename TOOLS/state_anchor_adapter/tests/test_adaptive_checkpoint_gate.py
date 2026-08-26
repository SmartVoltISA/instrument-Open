from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adaptive_checkpoint_gate import evaluate
from state_anchor_adapter import HardwareProfile

def host():
    return HardwareProfile('test','x86_64',8,16000,12000,100.0,None,None,0.5)

def test_normal_target():
    r=evaluate(host(),{},steps_since_anchor=0)
    assert not r['checkpoint_due'] and r['policy']['target_steps']==5

def test_contradiction_immediate():
    r=evaluate(host(),{'contradiction_count':1},steps_since_anchor=1)
    assert r['checkpoint_due'] and r['policy']['target_steps']==1

def test_maximum_absolute():
    r=evaluate(host(),{},steps_since_anchor=10)
    assert r['checkpoint_due'] and r['policy']['maximum_steps']==10
