# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Architecture

This is a Python-based command-line calculator with two main components:

- **src/calc/__main__.py**: Main calculator interface with expression parsing, time handling, and interactive shell
- **src/calc/evaluator.py**: Safe expression evaluation engine using AST (Abstract Syntax Tree) for security

The calculator uses a secure evaluation approach - it parses expressions into AST nodes and only allows predefined operators, functions, and constants to prevent arbitrary code execution.

## Key Features

- Interactive shell mode with history support (using `?` for previous result)
- Safe mathematical expression evaluation with whitelisted functions/operators
- Time calculations supporting `HH:MM:SS` format and seconds with `s`/`sec` units
- Number formatting with thousands separators
- Comment support (lines starting with `#`)
- Operator aliases: `x`/`X` for multiplication, `^` for exponentiation

## Common Development Commands

### Testing
```bash
make test           # Run all tests using pytest
./calc_debug pytest -p no:cacheprovider tests/test_calc.py  # Run tests directly
```

### Linting and Type Checking
```bash
make lint          # Run all linters (flake8, hadolint, shellcheck, shfmt)
make flake8        # Python linting only
make mypy          # Type checking
```

### Building
```bash
make build         # Build production Docker image
make build_dev     # Build development Docker image
```

### Requirements Management
```bash
make update_requirements      # Update requirements.txt
make update_requirements_dev  # Update requirements_dev.txt
```

### Running the Calculator
```bash
./calc                    # Interactive mode (containerized)
./calc "1 + 2 * 3"       # Direct calculation (containerized)
```

## Test Structure

Tests are in `tests/test_calc.py` and cover:
- Basic arithmetic operators and aliases
- Mathematical functions (sin, cos, sqrt, etc.)
- Constants (pi, e)
- Time calculations
- Comment handling
- Error conditions

When adding new features, add corresponding test cases following the existing pattern.

## Security Model

The evaluator uses a whitelist approach:
- `allowed_operators`: Only basic math operators (+, -, *, /, %, **)
- `allowed_functions`: Math functions, min/max, round, timedelta
- `allowed_constants`: Just pi and e

Never add functions that could execute arbitrary code or access the filesystem.

## Expression Processing Pipeline

1. **src/calc/__main__.py**: Parse comments, handle `?` substitution, convert time formats
2. **src/calc/evaluator.py**: Parse to AST and evaluate with security restrictions
3. **src/calc/__main__.py**: Format output (thousands separators, time formatting)

## Development Environment

The project uses containerized development with Docker. The `calc_debug` script runs tools in the development container for consistent environments across different systems.