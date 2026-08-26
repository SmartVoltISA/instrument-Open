#!/usr/bin/env python3
"""Portable Adaptive State Anchor Adapter v0.2.

External checkpointing for long-running processes.
Hardware is a reliability signal, never a proxy for model/LLM context.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

FOUNDATION_TARGET = 5
FOUNDATION_MAXIMUM = 10

@dataclass
class HardwareProfile:
    os: str
    arch: str
    cpu_logical: int
    ram_total_mb: int | None
    ram_available_mb: int | None
    disk_free_gb: float | None
    gpu_name: str | None
    gpu_vram_mb: int | None
    load_1m: float | None

@dataclass
class AnchorPolicy:
    target_steps: int
    maximum_steps: int
    pressure: float
    reason: list[str]

def _linux_meminfo() -> tuple[int | None, int | None]:
    try:
        values: dict[str, int] = {}
        for line in Path('/proc/meminfo').read_text().splitlines():
            k, v = line.split(':', 1)
            values[k] = int(v.strip().split()[0])
        total, available = values.get('MemTotal'), values.get('MemAvailable')
        return (total // 1024 if total else None, available // 1024 if available else None)
    except Exception:
        return None, None

def _psutil_memory() -> tuple[int | None, int | None]:
    try:
        import psutil
        m = psutil.virtual_memory()
        return int(m.total / 1024**2), int(m.available / 1024**2)
    except Exception:
        return None, None

def _gpu() -> tuple[str | None, int | None]:
    if not shutil.which('nvidia-smi'):
        return None, None
    try:
        lines = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'],
            text=True, stderr=subprocess.DEVNULL, timeout=2).strip().splitlines()
        if not lines:
            return None, None
        name, vram = [x.strip() for x in lines[0].split(',', 1)]
        return name, int(float(vram))
    except Exception:
        return None, None

def profile() -> HardwareProfile:
    total, available = _psutil_memory()
    if total is None and platform.system() == 'Linux':
        total, available = _linux_meminfo()
    try:
        disk_free = shutil.disk_usage(Path.home()).free / 1024**3
    except Exception:
        disk_free = None
    try:
        load = float(os.getloadavg()[0])
    except (AttributeError, OSError):
        load = None
    gpu_name, gpu_vram = _gpu()
    return HardwareProfile(platform.system(), platform.machine(), os.cpu_count() or 1,
                           total, available, disk_free, gpu_name, gpu_vram, load)

def resource_pressure(p: HardwareProfile) -> float:
    signals: list[float] = []
    if p.ram_total_mb and p.ram_available_mb:
        used = 1.0 - p.ram_available_mb / p.ram_total_mb
        signals.append(max(0.0, min(1.0, (used - 0.50) / 0.45)))
    if p.load_1m is not None and p.cpu_logical:
        signals.append(max(0.0, min(1.0, p.load_1m / p.cpu_logical)))
    if p.disk_free_gb is not None:
        signals.append(max(0.0, min(1.0, (10.0 - p.disk_free_gb) / 10.0)))
    return max(signals, default=0.0)

def policy(p: HardwareProfile, risk: str = 'normal', steps_since_anchor: int = 0,
           pressure: float | None = None) -> AnchorPolicy:
    pressure = resource_pressure(p) if pressure is None else max(0.0, min(1.0, pressure))
    target = FOUNDATION_TARGET
    reasons = ['default target = 5 steps']
    target = min(target, {'low': 7, 'normal': 5, 'high': 2, 'critical': 1}[risk])
    if risk != 'normal':
        reasons.append(f'{risk} process risk')
    if pressure >= 0.85:
        target = min(target, 1); reasons.append('critical host pressure')
    elif pressure >= 0.65:
        target = min(target, 2); reasons.append('high host pressure')
    elif pressure >= 0.40:
        target = min(target, 3); reasons.append('moderate host pressure')
    elif pressure >= 0.20:
        target = min(target, 4); reasons.append('elevated host pressure')
    if steps_since_anchor >= FOUNDATION_MAXIMUM:
        target = 1; reasons.append('maximum interval reached')
    elif steps_since_anchor >= FOUNDATION_TARGET:
        target = min(target, max(1, FOUNDATION_MAXIMUM - steps_since_anchor))
        reasons.append('checkpoint distance reached')
    return AnchorPolicy(max(1, min(target, FOUNDATION_MAXIMUM)), FOUNDATION_MAXIMUM, pressure, reasons)

def should_checkpoint(*, steps_since_anchor: int, policy_value: AnchorPolicy,
                      event: str | None = None) -> tuple[bool, str]:
    urgent = {'branch', 'decision', 'irreversible', 'external_write', 'error',
              'contradiction', 'recovery', 'uncertain'}
    if event in urgent:
        return True, f'early checkpoint: {event}'
    if steps_since_anchor >= policy_value.maximum_steps:
        return True, 'absolute maximum reached'
    if steps_since_anchor >= policy_value.target_steps:
        return True, 'adaptive target reached'
    return False, 'checkpoint not yet due'

def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')

def _digest(anchor_without_digest: dict) -> str:
    return hashlib.sha256(_canonical_json(anchor_without_digest)).hexdigest()

def make_anchor(state: dict, output_dir: str = '.anchors', *, step: int = 0,
                risk: str = 'normal', event: str | None = None) -> dict:
    p = profile()
    anchor = {
        'schema': 'state-anchor/v0.2',
        'checkpoint_id': f'anchor-{int(time.time_ns())}',
        'created_unix': time.time(),
        'hardware': asdict(p),
        'policy': asdict(policy(p, risk=risk, steps_since_anchor=step)),
        'event': event,
        'state': state,
    }
    anchor['digest_sha256'] = _digest(anchor)
    path = Path(output_dir); path.mkdir(parents=True, exist_ok=True)
    final = path / f"{anchor['checkpoint_id']}.json"
    tmp = final.with_suffix('.tmp')
    tmp.write_text(json.dumps(anchor, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, final)
    anchor['path'] = str(final)
    return anchor

def verify_anchor(anchor: dict) -> dict:
    expected = anchor.get('digest_sha256')
    copy = dict(anchor); copy.pop('digest_sha256', None)
    actual = _digest(copy)
    ok = bool(expected) and expected == actual
    return {'verified': ok, 'expected': expected, 'actual': actual,
            'status': 'VERIFIED' if ok else 'FAILED'}

def verify_anchor_file(path: str) -> dict:
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception as exc:
        return {'verified': False, 'status': 'FAILED', 'error': str(exc)}
    result = verify_anchor(data); result['path'] = path
    return result

def main() -> None:
    ap = argparse.ArgumentParser(description='Portable adaptive external state anchor tool')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('profile')
    pp = sub.add_parser('policy'); pp.add_argument('--risk', choices=['low','normal','high','critical'], default='normal'); pp.add_argument('--steps', type=int, default=0); pp.add_argument('--pressure', type=float, default=None)
    cp = sub.add_parser('checkpoint'); cp.add_argument('--state', required=True); cp.add_argument('--dir', default='.anchors'); cp.add_argument('--step', type=int, default=0); cp.add_argument('--risk', choices=['low','normal','high','critical'], default='normal'); cp.add_argument('--event', default=None)
    vp = sub.add_parser('verify'); vp.add_argument('path')
    args = ap.parse_args(); p = profile()
    if args.cmd == 'profile': print(json.dumps(asdict(p), ensure_ascii=False, indent=2))
    elif args.cmd == 'policy': print(json.dumps(asdict(policy(p, args.risk, args.steps, args.pressure)), ensure_ascii=False, indent=2))
    elif args.cmd == 'checkpoint': print(json.dumps(make_anchor(json.loads(args.state), args.dir, step=args.step, risk=args.risk, event=args.event), ensure_ascii=False, indent=2))
    elif args.cmd == 'verify': print(json.dumps(verify_anchor_file(args.path), ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
