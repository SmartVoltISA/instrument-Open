# Portable State Anchor Adapter — Activation Contract

The adapter is intended for long-running workflows.

## Trigger

Initialize it when a workflow has more than 5 steps, is an experiment, retains intermediate state, branches, performs external/irreversible writes, or may require recovery.

## Adaptive policy

`hardware profile + current resource pressure + process risk → checkpoint interval`

Target: 5 steps.
Maximum: 10 steps.
Risk or pressure may force an earlier checkpoint; it may never extend the maximum.

Hardware is a reliability signal, never a proxy for model/LLM context.

## Required lifecycle

`PROFILE → POLICY → WORK → STATE UPDATE → CHECKPOINT → VERIFY → CONTINUE`

On uncertainty:

`LATEST VERIFIED ANCHOR → VERIFY → RESTORE → MARK UNCERTAINTY → CONTINUE`

If the adapter is unavailable, the workflow must report degraded state rather than silently claiming protection.

## Privacy

This public adapter accepts only user-provided external input. It contains no project data or private project identifiers.
