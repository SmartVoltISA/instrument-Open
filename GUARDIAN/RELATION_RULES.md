# Relation Rules

## Core rule

A public tool may depend on another public tool, but it must not depend on a private application project.

Allowed:

`PUBLIC TOOL → PUBLIC TOOL`

`PROJECT → PUBLIC TOOL`

Forbidden:

`PUBLIC TOOL → PRIVATE PROJECT`

`PRIVATE PROJECT DATA → PUBLIC TOOL`

## Evidence rule

A claim about a tool must point to the tool's own implementation, test, fixture, CI result or documented limitation.

## Feedback rule

Feedback belongs to the tool version that produced the observed result. Feedback must not silently alter the tool or its provenance.

## State rule

Status follows evidence:

`IDEA → DEVELOPMENT → WORKING → VERIFIED → STABLE`

A source project's status does not automatically transfer to the portable public copy.

## Separation rule

If removing project-specific data breaks the tool, the dependency must be declared. The item is not portable until the dependency is replaced or deliberately retained as an external public dependency.
