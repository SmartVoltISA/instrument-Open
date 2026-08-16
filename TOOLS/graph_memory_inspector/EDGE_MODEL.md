# First-Class Edge Model v1.0

A connection is an independently inspectable object, not merely a pointer between nodes.

## Edge structure

```text
EDGE
├── id
├── source
├── target
├── type
├── provenance
└── history/state (future extension)
```

## Meaning

- `source` — where the relation starts;
- `target` — where it ends;
- `type` — what the relation means;
- `provenance` — where the relation came from;
- `id` — stable identity of the relation itself.

## Inspector checks

1. Edge has identity.
2. Source node exists.
3. Target node exists.
4. Edge has semantic type.
5. Edge has provenance.
6. Edge identity is not duplicated.
7. Identical source-target-type edges are not accidentally duplicated.
8. Inspection does not mutate the graph.

## Core relation

`node → edge → node`

The edge itself is an auditable unit.

## Validation boundary

The portable tool validates structural integrity. Validation against any particular application's data must be performed by the user of the tool and must not be embedded into this public copy.
