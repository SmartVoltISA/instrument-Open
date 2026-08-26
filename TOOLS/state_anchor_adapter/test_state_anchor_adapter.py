from pathlib import Path
import tempfile

from state_anchor_adapter import (
    AnchorPolicy, HardwareProfile, make_anchor, policy,
    should_checkpoint, verify_anchor_file,
)


def host() -> HardwareProfile:
    return HardwareProfile('test', 'test', 8, 16384, 12000, 100, None, None, 0.1)


def test_policy_never_exceeds_foundation_maximum():
    p = host()
    for risk in ('low', 'normal', 'high', 'critical'):
        for steps in (0, 4, 5, 9, 10, 100):
            assert 1 <= policy(p, risk, steps).target_steps <= 10
            assert policy(p, risk, steps).maximum_steps == 10


def test_urgent_event_forces_checkpoint():
    p = AnchorPolicy(5, 10, 0.0, [])
    assert should_checkpoint(steps_since_anchor=0, policy_value=p, event='decision')[0]


def test_anchor_roundtrip_and_digest_verification():
    with tempfile.TemporaryDirectory() as d:
        anchor = make_anchor({'objective': 'neutral-test', 'status': 'WORKING'}, d)
        result = verify_anchor_file(anchor['path'])
        assert result['verified'] is True
        assert Path(anchor['path']).exists()


def test_tampering_is_detected():
    with tempfile.TemporaryDirectory() as d:
        anchor = make_anchor({'objective': 'neutral-test', 'status': 'WORKING'}, d)
        path = Path(anchor['path'])
        text = path.read_text(encoding='utf-8').replace('WORKING', 'FAILED')
        path.write_text(text, encoding='utf-8')
        assert verify_anchor_file(str(path))['verified'] is False
