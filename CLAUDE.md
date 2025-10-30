# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Architecture

This is a Python-based command-line calculator with the following main components:

- `src/calc/__main__.py`: Main calculator interface with expression parsing, time handling, and interactive shell
- `src/calc/evaluator.py`: Safe expression evaluation engine using AST (Abstract Syntax Tree) for security
- `src/calc/time_utils.py`: Time expression conversion and formatting utilities
- `src/calc/help_text.py`: Help command text definitions

The calculator uses a secure evaluation approach - it parses expressions into AST nodes and only allows predefined operators, functions, and constants to prevent arbitrary code execution.

## Key Features

- Interactive shell mode with history support (using `?` for previous result)
- Built-in help system (`help` command)
- Safe mathematical expression evaluation with whitelisted functions/operators
- Comprehensive time calculations with natural language support:
  - Basic format: `HH:MM:SS[.ffffff]` (microseconds optional)
  - English units: `s`/`sec`/`seconds`, `m`/`min`/`minutes`, `h`/`hr`/`hours`, `d`/`day`/`days`
  - Japanese units: `秒`/`秒間`, `分`/`分間`, `時`/`時間`, `日`/`日間`
  - Compact combinations: `1h 30m`, `1m 5s`
  - Day combinations: `1 day and 10 hours`, `1 day and 1 hour 2 min`
  - Natural language: `1 day 2 hours 30 minutes`, `1時間 30分` (or `1時間30分`), `2日 3時間` (or `2日3時間`)
- Time output uses `and` format when time components exist: `1 day and 02:00:00`, or just `1 day` for whole days (with microseconds when present: `00:01:30.500000`)
- Number formatting with thousands separators
- Comment support (`#` and everything after it is ignored)
- Operator aliases:
  - Addition: `＋`
  - Subtraction: `－`
  - Multiplication: `x` `X` `×`
  - Division: `÷`
  - Exponentiation: `^` (alternative to `**`)
- Non-time unit removal: Units after numbers are ignored except for time units (e.g., `個`, `円`, `kg`, `GB`, `USD`)

## Common Development Commands

### Quick Commands

```bash
make all           # Lint, update requirements.txt, test, and build
make help          # Display all available make targets with descriptions
```

### Testing

```bash
make test          # Test Python code with pytest
```

### Linting and Type Checking

```bash
make lint          # Run all linters (ruff, hadolint, markdownlint, shellcheck, shfmt)
make ruff          # Lint Python code
make mypy          # Check Python types
make hadolint      # Lint Dockerfile
make markdownlint  # Lint Markdown files
make shellcheck    # Lint shell scripts
make shfmt         # Lint shell script formatting
```

### Building

```bash
make build         # Build image 'shakiyam/calc' from Dockerfile
make build_dev     # Build image 'shakiyam/calc_dev' from Dockerfile.dev
```

### Requirements Management

```bash
make update_requirements      # Update requirements.txt
make update_requirements_dev  # Update requirements_dev.txt
```

### Running the Calculator

```bash
./calc                   # Interactive mode (containerized)
./calc "1 + 2 * 3"       # Direct calculation (containerized)
```

## Test Structure

Tests are organized in multiple files under `tests/`:

- `test_basic.py` - Basic arithmetic, precision, comments, formatting, history
- `test_functions.py` - Mathematical functions and constants
- `test_time.py` - Time calculations and conversions
- `test_time_utils.py` - Time utilities and conversion functions
- `test_errors.py` - Error handling (syntax, security, runtime, arguments, time-related)

When adding new features, add corresponding test cases in the appropriate file following the existing pattern.

## Security Model

The evaluator uses a whitelist approach:

- `allowed_operators`: Only basic math operators (+, -, *, /, %, **)
- `allowed_functions`: Math functions, min/max, round, timedelta
- `allowed_constants`: Just pi and e

Never add functions that could execute arbitrary code or access the filesystem.

## Expression Processing Pipeline

1. `src/calc/__main__.py`: Parse comments, handle `?` substitution, convert time formats
2. `src/calc/evaluator.py`: Parse to AST and evaluate with security restrictions
3. `src/calc/__main__.py`: Format output (thousands separators, time formatting)

## Development Environment

The project uses containerized development with Docker. The `calc_debug` script runs tools in the development container for consistent environments across different systems.

## Documentation Maintenance

The project maintains feature documentation in multiple places with specific roles:

- **Help command** (`src/calc/help_text.py`): Quick reference for users during calculator use - minimal content only
- **README.md**: Detailed user documentation with examples for all features
- **CLAUDE.md**: Architecture, development commands, and implementation details for AI/developers

### Feature Addition Checklist

When adding new features, update documentation as follows:

- [ ] Add tests in appropriate `tests/test_*.py` file (test-first)
- [ ] Implement feature code
- [ ] Run `make lint` to ensure code quality
- [ ] Run `make test` to verify all tests pass
- [ ] Update help command in `src/calc/help_text.py` (if user-facing)
- [ ] Update README.md with examples and detailed explanations
- [ ] Update CLAUDE.md as needed (architecture, features, test structure, etc.)
- [ ] Run `make all` for final verification (lint, mypy, test, requirements, build)
