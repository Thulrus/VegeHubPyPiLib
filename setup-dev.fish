#!/usr/bin/env fish
# Development setup script for VegeHub library
# Run this after cloning the repository

echo "🚀 Setting up VegeHub development environment..."
echo ""

# Install dependencies
echo "📦 Installing dependencies with Poetry..."
poetry install

if test $status -ne 0
    echo "❌ Failed to install dependencies"
    exit 1
end

echo ""

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
poetry run pre-commit install

if test $status -ne 0
    echo "❌ Failed to install pre-commit hooks"
    exit 1
end

echo ""

# Run pre-commit on all files to set up environments
echo "🔍 Running pre-commit hooks for the first time (this may take a minute)..."
poetry run pre-commit run --all-files

# Don't fail if pre-commit makes changes, just inform
if test $status -ne 0
    echo ""
    echo "⚠️  Pre-commit hooks modified some files or found issues."
    echo "   This is normal on first run. Review the changes and commit them."
else
    echo ""
    echo "✅ All pre-commit checks passed!"
end

echo ""
echo "✨ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "  1. Run tests: poetry run pytest"
echo "  2. Make changes and commit: git commit -m 'Your message'"
echo "  3. Pre-commit hooks will run automatically on each commit"
echo ""
echo "Useful commands:"
echo "  poetry run pytest                      # Run tests"
echo "  poetry run pre-commit run --all-files  # Run all hooks manually"
echo "  poetry run pylint vegehub tests        # Run linter"
echo "  poetry run mypy vegehub                # Run type checker"
