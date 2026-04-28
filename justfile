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

# Run game
run:
    uv run pygbag src/mud/main.py

# Build game for distribution
build:
    uv run pygbag --build --archive src/mud/main.py
