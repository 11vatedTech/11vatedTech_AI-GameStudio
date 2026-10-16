# Contributing

## Principles

- Keep core execution local-first and dependency-light.
- Prefer explicit ports/adapters, immutable configuration, workspace-contained outputs, deterministic transformations, and recorded evidence.
- Preserve capability status distinctions. Tests with mocked provider responses are not full external integration tests.
- Add or update JSON Schema contracts, agent instructions, skill guidance, and tests when behavior or interface contracts change.
- Use upstream sources for model and tool claims. Track model weights separately from code licenses.
- Avoid checked-in model weights, credentials, databases, caches, engine outputs, or generated data that cannot be redistributed.

## Development

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
ags doctor
```

For a provider change, add protocol tests with deterministic mock responses and document the real-server checks required. For an image-processing change, add tests for alpha, edge cases, and source preservation. For a new capability, update `docs/capability-register.json` and keep its implementation status honest.

## Style and compatibility

Python 3.11+; type hints for public interfaces; no global mutable configuration; no shell execution with user-generated command text; bounded subprocess timeouts; actionable error codes; no tests that require downloaded model weights or paid services.
