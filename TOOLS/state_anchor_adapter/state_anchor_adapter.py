#!/usr/bin/env python3
"""State Anchor Adapter v0.1

Dependency-light reference implementation.
Measures host resources and converts them into a conservative checkpoint
interval. Hardware is a reliability signal, not a proxy for model context.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path


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
    reason: list[str]


def _linux_meminfo() -> tuple[int | None, int | None]:
    try:
        data = Path('/proc/meminfo').read_text().splitlines()
        values = {}
        for line in data:
            k, v = line.split(':', 1)
            values[k] = int(v.strip().split()[0])  # kB
        total = values.get('MemTotal')
        available = values.get('MemAvailable')
        return (total // 1024 if total else None,
                available // 1024 if available else None)
    except Exception:
        return None, None


def _psutil_memory() -> tuple[int | None, int | None]:
    try:
        import psutil  # optional
        m = psutil.virtual_memory()
        return int(m.total / 1024**2), int(m.available / 1024**2)
    except Exception:
        return None, None


def _gpu() -> tuple[str | None, int | None]:
    if not shutil.which('nvidia-smi'):
        return None, None
    try:
        out = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=name,memory.total',
             '--format=csv,noheader,nounits'],
            text=True, stderr=subprocess.DEVNULL, timeout=2,
        ).strip().splitlines()[0]
        name, vram = [x.strip() for x in out.split(',', 1)]
        return name, int(float(vram))
    except Exception:
        return None, None


def profile() -> HardwareProfile:
    total, available = _psutil_memory()
    if total is None and platform.system() == 'Linux':
        total, available = _linux_meminfo()

    disk_free = None
    try:
        disk_free = shutil.disk_usage(Path.home()).free / 1024**3
    except Exception:
        pass

    load = None
    try:
        load = float(os.getloadavg()[0])
    except (AttributeError, OSError):
        pass

    gpu_name, gpu_vram = _gpu()

    return HardwareProfile(
        os=platform.system(),
        arch=platform.machine(),
        cpu_logical=os.cpu_count() or 1,
        ram_total_mb=total,
        ram_available_mb=available,
        disk_free_gb=disk_free,
        gpu_name=gpu_name,
        gpu_vram_mb=gpu_vram,
        load_1m=load,
    )


def policy(p: HardwareProfile, risk: str = 'normal') -> AnchorPolicy:
    """Return a conservative 1..10 step policy.

    Thresholds are engineering heuristics and must be validated on real
    devices before promotion to VERIFIED/STABLE.
    """
    target = 5
    reasons: list[str] = ['Foundation default target = 5 steps']

    # Hardware capacity is used only as a safety factor.
    if p.ram_total_mb is not None:
        if p.ram_total_mb < 8192:
            target = min(target, 3)
            reasons.append('RAM < 8 GB: conservative interval')
        elif p.ram_total_mb < 16384:
            target = min(target, 4)
            reasons.append('RAM < 16 GB: conservative interval')
        elif p.ram_total_mb >= 32768:
            target = min(7, target + 2)
            reasons.append('RAM >= 32 GB: capacity permits longer target')

    if p.cpu_logical <= 2:
        target = min(target, 3)
        reasons.append('<= 2 logical CPU cores')
    elif p.cpu_logical <= 4:
        target = min(target, 4)
        reasons.append('<= 4 logical CPU cores')

    if p.ram_total_mb and p.ram_available_mb:
        available_ratio = p.ram_available_mb / p.ram_total_mb
        if available_ratio < 0.15:
            target = min(target, 2)
            reasons.append('low currently available RAM')
        elif available_ratio < 0.25:
            target = min(target, 3)
            reasons.append('moderate RAM pressure')

    if p.load_1m is not None and p.cpu_logical:
        load_ratio = p.load_1m / p.cpu_logical
        if load_ratio > 1.0:
            target = min(target, 2)
            reasons.append('CPU load exceeds logical-core capacity')
        elif load_ratio > 0.75:
            target = min(target, 3)
            reasons.append('high CPU load')

    if p.disk_free_gb is not None and p.disk_free_gb < 2:
        target = 1
        reasons.append('critically low disk space')
    elif p.disk_free_gb is not None and p.disk_free_gb < 10:
        target = min(target, 3)
        reasons.append('low disk space')

    if risk == 'high':
        target = min(target, 2)
        reasons.append('high process risk')
    elif risk == 'critical':
        target = 1
        reasons.append('critical process risk')
    elif risk == 'low':
        target = min(target + 1, 7)
        reasons.append('low process risk')

    return AnchorPolicy(target_steps=max(1, min(target, 10)),
                        maximum_steps=10,
                        reason=reasons)


def make_anchor(state: dict, output_dir: str = '.anchors') -> dict:
    """Create a durable JSON anchor with hardware and timestamp."""
    p = profile()
    anchor = {
        'checkpoint_id': f"anchor-{int(time.time())}",
        'created_unix': time.time(),
        'hardware': asdict(p),
        'state': state,
    }
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    final = path / f"{anchor['checkpoint_id']}.json"
    tmp = final.with_suffix('.tmp')
    tmp.write_text(json.dumps(anchor, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, final)  # atomic on the same filesystem
    anchor['path'] = str(final)
    return anchor


def main() -> None:
    ap = argparse.ArgumentParser(description='Adaptive external state anchor tool')
    sub = ap.add_subparsers(dest='cmd', required=True)

    sub.add_parser('profile', help='print detected hardware profile')

    pp = sub.add_parser('policy', help='calculate checkpoint interval')
    pp.add_argument('--risk', choices=['low', 'normal', 'high', 'critical'], default='normal')

    cp = sub.add_parser('checkpoint', help='write a JSON state anchor')
    cp.add_argument('--state', required=True, help='JSON object describing current state')
    cp.add_argument('--dir', default='.anchors')

    args = ap.parse_args()
    p = profile()

    if args.cmd == 'profile':
        print(json.dumps(asdict(p), ensure_ascii=False, indent=2))
    elif args.cmd == 'policy':
        print(json.dumps(asdict(policy(p, args.risk)), ensure_ascii=False, indent=2))
    elif args.cmd == 'checkpoint':
        state = json.loads(args.state)
        print(json.dumps(make_anchor(state, args.dir), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
