# Portable Tool Chain

## Purpose

This document defines the mandatory relationship chain for extracting a tool from any private or project repository into the public instrument layer.

## Chain

`SOURCE → EXTRACT → ISOLATE → SANITIZE → VERIFY → PORTABLE → PUBLISH`

## 1. SOURCE

Record the original repository, path, version/commit and required source files.

## 2. EXTRACT

Identify only the reusable tool components: implementation, tests, fixtures, interface documentation and CI needed to reproduce the tool's own validation.

## 3. ISOLATE

Separate the tool from project-specific code, data, configuration, paths, names, secrets and integrations.

## 4. SANITIZE

Remove project data and internal identifiers. Replace real user/project inputs with neutral examples or explicit placeholders such as `<USER_DATA>`.

## 5. VERIFY

Check that the isolated copy still has a complete interface and that its tests can run without the source project.

## 6. PORTABLE

The resulting tool must have:

- a clear input interface;
- a clear output interface;
- connection instructions;
- usage example with non-project data;
- tests;
- limitations;
- provenance to the source version.

## 7. PUBLISH

Only the portable result enters the public repository.

## Prohibited relation

`PRIVATE PROJECT DATA → PUBLIC TOOL`

This relation is forbidden.

## Required provenance

Every portable tool records:

`source repository → source path → source revision → extracted components → Guardian check → portable revision`

## Status gate

No tool may be marked `VERIFIED` merely because the source version worked. The portable copy must pass its own reproducible verification.
