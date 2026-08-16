# CI validation

## Portable validation gate

The public copy must independently run the same executable test suite that validates the tool source.

Command:

```bash
python -m unittest -v test_inspector.py
```

Recommended runtime: Python 3.12, matching the source validation workflow.

## Promotion rule

`WORKING` → `VERIFIED` only after the public repository CI produces a successful run for this path.

The source repository's successful CI is recorded as provenance, not reused as evidence for the public copy.

## Required evidence

The public validation must show:

- test command executed;
- runtime version;
- test count/result;
- successful exit status;
- commit/revision being tested.

## Failure handling

If CI fails, retain `WORKING` or move to `FAILED` according to the failure. Do not mark `VERIFIED` until a later run passes.
