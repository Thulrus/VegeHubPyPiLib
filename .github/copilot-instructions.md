# GitHub Copilot Instructions for VegeHub Library

## Project Overview

This is a Python library for interacting with Vegetronix VegeHub devices - IoT relay controllers that manage sensors and actuators. The library provides an async HTTP API client for:
- Device discovery via mDNS
- Reading device info and status
- Controlling actuators (relays)
- Configuring device endpoints
- Supporting both old and new firmware versions

**Primary Use Case**: Home Assistant integration for VegeHub devices

## Development Environment

### Package Manager: Poetry
This project uses **Poetry** for dependency management, NOT pip or venv directly.

```fish
# Install dependencies
poetry install

# Add a dependency
poetry add package-name

# Add a dev dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Run commands in the Poetry environment
poetry run python script.py
poetry run pytest
```

### Shell: Fish
The development environment uses **fish shell**, NOT bash. When generating shell commands:

**✅ Do this (fish):**
```fish
set MY_VAR "value"
echo $MY_VAR
```

**❌ Not this (bash):**
```bash
export MY_VAR="value"
echo $MY_VAR
```

**Important**: Fish does NOT support heredocs. Use `printf` or `echo` instead.

## Project Structure

```
VegeHubPyPiLib/
├── vegehub/              # Main library code
│   ├── __init__.py       # Package initialization
│   ├── vegehub.py        # VegeHub class (main API)
│   └── helpers.py        # Helper functions
├── tests/                # Unit tests (pytest)
│   ├── test_vegehub.py   # VegeHub class tests
│   └── test_helpers.py   # Helper function tests
├── integration_test.py   # Integration tests (run against real devices)
├── doc/
│   └── AI/              # AI-generated documentation and summaries
├── pyproject.toml       # Poetry config, dependencies, test config
├── README.md            # User documentation
├── CHANGELOG.md         # Version history
└── Walkthrough.md       # Development guide
```

## Testing

### Pre-Commit Hooks (Recommended Workflow)
This project uses **pre-commit hooks** to catch issues before they reach CI:

```fish
# Hooks run automatically on every commit
git commit -m "Your message"

# Run all hooks manually
poetry run pre-commit run --all-files

# Run hooks on staged files only
poetry run pre-commit run
```

Pre-commit automatically runs:
- **Formatting**: Black (code) and isort (imports)
- **Tests**: All 70 unit tests with pytest
- **Linting**: pylint for code quality
- **Type checking**: mypy for type hints
- **File checks**: Trailing whitespace, line endings, etc.

If any check fails, the commit is blocked until you fix it. This prevents CI failures.

### Unit Tests
Run unit tests with pytest (70 tests, 100% coverage):

```fish
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run with coverage report
poetry run pytest --cov=vegehub --cov-report=html --cov-report=term

# Run specific test file
poetry run pytest tests/test_vegehub.py

# Run specific test
poetry run pytest tests/test_vegehub.py::test_name
```

### Integration Tests
Integration tests run against real VegeHub devices on the network:

```fish
# Run integration tests (requires real device)
poetry run python integration_test.py
```

**Note**: `integration_test.py` is excluded from coverage reports (see pyproject.toml).

### VS Code Tasks
Pre-configured tasks available (Ctrl+Shift+P → "Run Task"):
- Run Tests
- Run Tests with Coverage
- Run Linter (pylint)
- Run Type Checker (mypy)
- Run All Checks
- Build Package
- Run Integration Tests

## Code Standards

### Type Hints
Use type hints everywhere (checked with mypy):

```python
async def get_info(self) -> dict | None:
    """Docstring here."""
    ...
```

### Async/Await
The library is **fully async** using aiohttp:

```python
async def example():
    hub = VegeHub(ip_address="192.168.0.100")
    info = await hub._get_device_info()
    await hub.close()  # Clean up if no session provided
```

### Session Management
**Important**: The library supports session reuse for better performance:

```python
# Recommended: Share a session
async with aiohttp.ClientSession() as session:
    hub = VegeHub(ip_address="...", session=session)
    # Use hub...
# Session auto-closes

# Alternative: Library creates its own
hub = VegeHub(ip_address="...")
try:
    # Use hub...
finally:
    await hub.close()  # Must close manually!
```

### Testing Patterns

**Async fixtures** (for cleanup):
```python
import pytest_asyncio

@pytest_asyncio.fixture
async def hub():
    h = VegeHub(ip_address="192.168.0.100")
    yield h
    await h.close()  # Cleanup
```

**Mocking HTTP** (use aioresponses):
```python
from aioresponses import aioresponses

async def test_something():
    with aioresponses() as mocked:
        mocked.post("http://192.168.0.100/api/info/get",
                    payload={"hub": {...}})
        # Test code here
```

## Linting & Type Checking

```fish
# Run pylint
poetry run pylint vegehub tests

# Run mypy
poetry run mypy vegehub

# Run all checks
poetry run pytest && poetry run pylint vegehub tests && poetry run mypy vegehub
```

**Note**: Some pylint warnings are intentionally disabled:
- `protected-access` in tests (accessing `_private` methods)
- `broad-except` in integration_test.py (user-friendly error handling)

## Documentation Guidelines

### Code Documentation
- All public methods need docstrings
- Use Google-style docstrings
- Include type hints in addition to docstrings

### AI-Generated Documentation
When creating summary documents or troubleshooting guides, save them to:

```
doc/AI/
```

This keeps the project root clean. Include:
- Problem description
- Root cause analysis
- Solution implemented
- Before/after comparisons

See `doc/AI/README.md` for examples of existing documentation.

## VegeHub API Specifics

### Firmware Versions
The library supports two firmware versions:

**Old firmware:**
```python
config = {
    "hub": [{"server": "...", "enabled": True}],
    "api_key": [{"key": "..."}]
}
```

**New firmware:**
```python
config = {
    "endpoints": [
        {"id": 1, "type": "mqtt", "enabled": True, ...}
    ]
}
```

**Detecting firmware type:**
```python
endpoints = config.get("endpoints")
if isinstance(endpoints, list):  # Not None, could be []
    # New firmware
else:
    # Old firmware (endpoints is None)
```

### HTTP Endpoints
All endpoints use POST with JSON payloads:
- `/api/info/get` - Device information
- `/api/config/get` - Configuration
- `/api/config/set` - Update configuration
- `/api/actuators/status` - Actuator states
- `/api/actuators/set` - Control actuators

### Error Handling
All HTTP methods raise `ConnectionError` on failure:

```python
try:
    await hub.retrieve_mac_address(retries=2)
except ConnectionError:
    # Handle connection failure
```

## Building & Publishing

```fish
# Validate pyproject.toml
poetry check

# Build package
poetry build

# Publish to TestPyPI
poetry publish --build --repository testpypi

# Publish to PyPI
poetry publish --build
```

**Version**: Update in `pyproject.toml` before publishing.

## Common Pitfalls

### ❌ Don't create sessions per request
```python
# BAD - creates new session every time
async def get_info(self):
    async with aiohttp.ClientSession() as session:
        response = await session.post(...)
```

### ✅ Do reuse sessions
```python
# GOOD - reuse session passed to constructor
async def get_info(self):
    session = await self._get_session()
    response = await session.post(...)
```

### ❌ Don't forget to close sessions
```python
# BAD - session never closed
hub = VegeHub(ip_address="...")
await hub._get_device_info()
```

### ✅ Do clean up properly
```python
# GOOD - session properly cleaned up
async with aiohttp.ClientSession() as session:
    hub = VegeHub(ip_address="...", session=session)
    await hub._get_device_info()
```

### ❌ Don't check dict keys for None values
```python
# BAD - returns True even if value is None
if "endpoints" in config:
    # This runs even when endpoints=None!
```

### ✅ Do check the actual value type
```python
# GOOD - distinguishes None from []
if isinstance(config.get("endpoints"), list):
    # Only runs when endpoints is actually a list
```

## Useful Commands Reference

```fish
# Full test suite with coverage
poetry run pytest --cov=vegehub --cov-report=html --cov-report=term

# Lint everything
poetry run pylint vegehub tests

# Type check
poetry run mypy vegehub

# Run integration tests
poetry run python integration_test.py

# Clean build artifacts
rm -rf dist/ build/ *.egg-info htmlcov/ .coverage .pytest_cache/ .mypy_cache/

# Show installed packages
poetry show

# Update all dependencies
poetry update
```

## Getting Help

- **README.md**: User-facing documentation
- **Walkthrough.md**: Development guide
- **doc/AI/**: Detailed technical documentation of fixes and enhancements
- **tests/**: Examples of usage patterns
- **integration_test.py**: Real-world usage example

## Key Design Principles

1. **Async everywhere** - All I/O is async
2. **Session reuse** - Share ClientSession for performance
3. **Firmware agnostic** - Support both old and new firmware
4. **Clean resource management** - Always close what you open
5. **Type safety** - Full type hints for mypy checking
6. **100% test coverage** - Every line of library code tested
7. **Real device testing** - Integration tests catch real-world issues

## When Making Changes

1. **Write tests first** - Maintain 100% coverage
2. **Check both firmware types** - Test old and new formats
3. **Run full test suite** - `poetry run pytest`
4. **Update CHANGELOG.md** - Document user-facing changes
5. **Type check** - `poetry run mypy vegehub`
6. **Lint** - `poetry run pylint vegehub tests`
7. **Test integration** - Run against real device if API changed
8. **Document** - Add AI summaries to `doc/AI/` if needed

## Integration Test Development Notes

The integration test suite was developed iteratively, discovering and fixing several issues:
- mDNS/asyncio threading conflicts
- Config format detection for different firmware
- Session cleanup and resource management
- Actuator control verification

See `doc/AI/README.md` for detailed history of these fixes.
