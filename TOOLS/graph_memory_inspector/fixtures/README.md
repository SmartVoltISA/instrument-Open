# Validation fixtures

The portable validation set uses six deterministic cases:

- `clean` — valid graph, no findings expected;
- `duplicate_node` — repeated identity;
- `conflicting_state` — incompatible state claims for one identity;
- `missing_provenance` — node or relation without provenance;
- `dangling_edge` — relation references a missing node;
- `mixed_failures` — several defects in one graph.

The fixtures contain only synthetic/user-supplied data. No project data is required.

A complete validation should record the expected finding set and verify that the input graph remains unchanged after inspection.
