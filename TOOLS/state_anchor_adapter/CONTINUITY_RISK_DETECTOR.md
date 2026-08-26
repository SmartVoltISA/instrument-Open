# Portable Continuity Risk Detector v0.1

STATUS: EXPERIMENTAL / PORTABLE

The detector scores only explicit process/state signals:
- checkpoint distance;
- unresolved/unknown items;
- contradictions/errors;
- branching/decision growth;
- state growth/completeness;
- verification age;
- recent state change.

Output: `NORMAL → WATCH → ELEVATED → CRITICAL` plus a recommended checkpoint target and an immediate-checkpoint flag.

It does not inspect model internals and does not claim to measure model context or memory capacity.

Foundation safety limits remain absolute: target 5, maximum 10; risk can only move the checkpoint earlier.

Thresholds are experimental heuristics and require calibration on real workflows and devices before stable verification.
