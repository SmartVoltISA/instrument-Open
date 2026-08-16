# Provenance

**Tool:** Graph Memory Inspector v0.1

## Source

- Repository: `SmartVoltISA/Omega-lab-.--.-`
- Source path: `tools/graph_memory_inspector/`
- Source revision: `dce12d01d3a77906855bacea8062c696de264047`

## Source components identified

- `inspector.py`
- `test_inspector.py`
- `README.md`
- `EDGE_MODEL.md`
- `fixtures/README.md`
- `.github/workflows/graph-memory-inspector.yml`

## Portable boundary

The public copy contains the reusable inspector logic, executable tests and tool-level validation documentation. Project-specific data and application-level integrations are excluded.

## Input boundary

The public user supplies their own graph as `graph`.

## Verification boundary

The source contains an executable test suite and a Python 3.12 GitHub Actions workflow. The portable copy must pass its own CI before being promoted from `WORKING` to `VERIFIED`.

## Important distinction

The existence of a passing source CI does not by itself prove that the public copy has passed an independent public CI run.
