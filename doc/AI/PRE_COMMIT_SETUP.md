# Pre-Commit Hooks Setup

## Overview

This project now uses **pre-commit hooks** to catch issues **before** they reach GitHub CI, saving time and preventing failed builds.

## What Happens When You Commit

Every time you run `git commit`, the following checks run **automatically**:

### 1. File Quality Checks
- ✂️ Trim trailing whitespace
- 📄 Fix end of file formatting
- ✅ Validate YAML syntax
- 🚫 Reject large files (>1MB)
- 🔀 Detect merge conflicts
- 📏 Normalize line endings

### 2. Code Formatting (Auto-Fix)
- **Black** - Reformats Python code to consistent style
- **isort** - Sorts imports alphabetically and by category

### 3. Testing & Quality
- **pytest** - Runs all 70 unit tests
- **pylint** - Checks code quality (must score >9.5/10)
- **mypy** - Validates type hints

If any check **fails**, the commit is **blocked** until you fix it.

## Installation (Already Done)

The hooks are already installed! But if you need to reinstall:

```fish
poetry run pre-commit install
```

## Usage

### Normal Workflow

Just commit as usual:

```fish
git add .
git commit -m "Your message"
# Hooks run automatically here!
```

If hooks fail, fix the issues and try again:

```fish
# Fix the issues in your editor
git add .
git commit -m "Your message"
# Hooks run again
```

### Skipping Hooks (Emergency Only)

If you absolutely must skip hooks (not recommended):

```fish
git commit --no-verify -m "Emergency commit"
```

### Running Hooks Manually

Check all files without committing:

```fish
poetry run pre-commit run --all-files
```

Check only staged files:

```fish
poetry run pre-commit run
```

### Updating Hooks

Update to latest hook versions:

```fish
poetry run pre-commit autoupdate
```

## What Gets Auto-Fixed

Some hooks **automatically fix** issues:

- Trailing whitespace removed
- Missing newlines at end of files added
- Line endings normalized
- **Code formatted with Black**
- **Imports sorted with isort**

After auto-fix, you'll see:

```
Format code with Black...................................................Failed
- hook id: black
- files were modified by this hook
```

This is normal! Just run `git add .` and commit again.

## Configuration Files

- `.pre-commit-config.yaml` - Hook definitions
- `pyproject.toml` - Tool configurations (Black, isort, pytest, etc.)

## Benefits Over CI-Only

### Before (CI-Only)
1. Write code
2. Commit and push
3. Wait 2-3 minutes for CI
4. See failure ❌
5. Fix locally
6. Commit and push again
7. Wait 2-3 minutes again
8. Finally passes ✅

**Total time: ~5+ minutes per mistake**

### After (Pre-Commit Hooks)
1. Write code
2. Commit (hooks run in 30-60 seconds)
3. If fail: Fix immediately
4. Commit again (hooks run again)
5. Push with confidence
6. CI passes first time ✅

**Total time: ~1-2 minutes, no CI retries needed**

## Performance

First run after install: ~2 minutes (installs environments)
Subsequent runs: ~30-60 seconds (cached)

The hooks use caching, so they're much faster than running commands manually.

## Differences from CI

### Pre-Commit Runs Locally
- All tests on your current Python version
- Checks your working directory
- Blocks bad commits

### CI Runs on GitHub
- Tests on Python 3.12 **and** 3.13
- Checks the pushed code
- Prevents bad merges

Both are important! Pre-commit catches issues early, CI ensures cross-platform compatibility.

## Black & isort Formatting

### Black
Opinionated Python formatter that enforces a consistent style:
- Line length: 88 characters (default)
- Double quotes for strings
- Consistent spacing

### isort
Sorts and organizes imports:
- Standard library first
- Third-party packages second
- Local imports last
- Alphabetical within each group

Both tools are configured to work together (isort uses "black" profile).

## Troubleshooting

### Hooks are slow
The first run installs environments. Subsequent runs are cached and faster.

### Hooks keep failing on formatting
Let Black and isort fix it automatically:

```fish
poetry run black vegehub tests integration_test.py
poetry run isort vegehub tests integration_test.py
git add .
git commit -m "Your message"
```

### Want to see what changed
Use `git diff` after hooks auto-fix:

```fish
git add .
git commit -m "Your message"
# Hooks modify files
git diff  # See what changed
git add .
git commit -m "Your message"  # Try again
```

### Pytest fails
Run tests manually to see details:

```fish
poetry run pytest -v
```

Fix the failing test, then commit again.

### Pylint fails
Run pylint to see all issues:

```fish
poetry run pylint vegehub tests
```

Fix the issues or add `# pylint: disable=rule-name` comments if justified.

## Disabling Specific Hooks

Edit `.pre-commit-config.yaml` and comment out hooks you don't want:

```yaml
  # - id: black  # Disabled
  #   name: Format code with Black
```

Then reinstall:

```fish
poetry run pre-commit install
```

## Adding New Hooks

Browse available hooks at:
- https://pre-commit.com/hooks.html
- https://github.com/pre-commit/pre-commit-hooks

Add to `.pre-commit-config.yaml` and run `pre-commit install`.

## Integration with VS Code

VS Code tasks still work! The pre-commit hooks and tasks are complementary:

**VS Code Tasks**: Run on-demand during development
**Pre-Commit Hooks**: Run automatically before commits

Use whatever workflow feels best!

## Summary

Pre-commit hooks shift quality checks **left** in your development workflow:

```
Write Code → [PRE-COMMIT HOOKS] → Commit → Push → [CI] → Merge
             ↑                                    ↑
             Catches most issues                  Final safety net
             Fast feedback                        Cross-version testing
```

This is the **industry standard** for professional Python projects. You'll see pre-commit in virtually all major open-source Python libraries.

## Commands Reference

```fish
# Install hooks (already done)
poetry run pre-commit install

# Run all hooks manually
poetry run pre-commit run --all-files

# Run hooks on staged files only
poetry run pre-commit run

# Update hooks to latest versions
poetry run pre-commit autoupdate

# Uninstall hooks
poetry run pre-commit uninstall

# Format code manually (before committing)
poetry run black vegehub tests integration_test.py
poetry run isort vegehub tests integration_test.py

# Check what will happen without modifying
poetry run black --check vegehub tests
poetry run isort --check vegehub tests
```
