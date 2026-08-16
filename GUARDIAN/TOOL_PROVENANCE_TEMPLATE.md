# Tool Provenance Record

**Tool ID:** `TOOL-XXX`

## Source

- Repository: `<SOURCE_REPOSITORY>`
- Path: `<SOURCE_PATH>`
- Revision: `<SOURCE_COMMIT_OR_TAG>`

## Extracted components

- implementation;
- tests;
- fixtures;
- documentation;
- CI/validation.

## Removed

- project data;
- private identifiers;
- project-specific paths;
- secrets and credentials;
- private integrations;
- dependencies that are not part of the tool itself.

## Portable interface

**Input:** `<USER_DATA>`

**Output:** `<TOOL_OUTPUT>`

## Guardian result

- Isolation: `PASS / FAIL`
- Project-data removal: `PASS / FAIL`
- Dependency check: `PASS / FAIL`
- Portable tests: `PASS / FAIL`
- Public release: `PASS / FAIL`

## Resulting revision

`<PUBLIC_REVISION>`

## Rule

The provenance record describes the lineage of the **tool**, not the private contents of the source project.
