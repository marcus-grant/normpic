# NormPic developer task runner.
#
# Developer-facing only. These recipes are not an integration
# interface: downstream callers invoke the CLI directly, not
# these recipes, so a rename here never breaks a caller.

# List available recipes.
default:
    @just --list

# Run the full test suite.
test:
    uv run pytest

# Lint with ruff.
lint:
    uv run ruff check

# Type check with pyright.
typecheck:
    uv run pyright

# Validate the canonical schema parses and is valid Draft 2020-12.
schema:
    uv run python script/check_schema.py

# The pre-commit quality gate, in the order doc/CONTRIBUTE.md
# defines it. Keep in step with that document.
check: lint typecheck test