# Simple DI Container

## How to run tests
- Run all tests: `python3 -m unittest discover tests -v`
- Run a specific test file: `python3 -m unittest tests.test_scopes -v`

## Key facts
- Only one module: `simple_di_container/container.py`
- Main entrypoint: `Container` class in `simple_di_container.container`
- Supports three scope types: singleton (default), transient, scoped
- All existing functionality preserved for backward compatibility
- Scope management: `create_scope()` and `destroy_scope()` methods
- Python 3.9+ required (uses type hints in documentation)