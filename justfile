#!/usr/bin/env just --justfile

# Default command
default:
    just -l

# Reformat and lint
format:
    uvx ruff@latest format .
    uvx ruff@latest check . --fix
    uvx uv-sort pyproject.toml
    bunx prettier --write "**/*.yaml" "**/*.yml"

# Run type checking
check *ARGS:
    uvx ty@latest check --output-format concise {{ARGS}}

# Run unit tests
test *ARGS:
    uv run pytest

# Run game
run *ARGS:
    uv run pygbag {{ARGS}} src

# Build game for distribution
build *ARGS:
    uv run pygbag --build --archive {{ARGS}} src
