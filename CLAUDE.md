# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Key Features

- Comment support (`#`)
- Operator aliases (`＋`, `－`, `×`, `÷`, `^`)
- Time calculations with English/Japanese natural language support
- Interactive shell with history (`?` for previous result)
- Number formatting with thousands separators
- Unit handling (non-time units like `個`, `円`, `kg` are ignored)
- Help command (`help`)

## Project Structure

```text
calc/
├── src/calc/              # Main source code
│   ├── __main__.py        # Entry point, expression parsing, shell
│   ├── evaluator.py       # Safe AST-based expression evaluation
│   ├── time_utils.py      # Time expression utilities
│   ├── help_text.py       # Help command text
│   └── py.typed           # PEP 561 marker
├── tests/                 # Test files
│   ├── test_basic.py      # Arithmetic, comments, formatting, history
│   ├── test_functions.py  # Math functions and constants
│   ├── test_time.py       # Time calculations
│   ├── test_time_utils.py # Time utilities
│   └── test_errors.py     # Error handling
├── tools/                 # Build and lint scripts
├── .github/               # GitHub Actions workflows
├── Dockerfile             # Production image
├── Dockerfile.dev         # Development image
├── Makefile               # Build automation
└── pyproject.toml         # Project configuration
```

## Architecture

Python-based command-line calculator with secure expression evaluation using AST (Abstract Syntax Tree) parsing.

**Processing Pipeline**:

1. `src/calc/__main__.py`: Parse comments, handle `?` substitution, convert time formats
2. `src/calc/evaluator.py`: Parse to AST and evaluate with security restrictions
3. `src/calc/__main__.py`: Format output (thousands separators, time formatting)

**Security Model**: The evaluator uses a whitelist approach:

- `allowed_operators`: Only basic math operators (+, -, *, /, %, **)
- `allowed_functions`: Math, rounding, and aggregate functions, timedelta
- `allowed_constants`: Just pi and e

Never add functions that could execute arbitrary code or access the filesystem.

## Code Style

- **Python**: 3.10+ with type hints required (mypy strict mode)
- **Line Length**: 100 characters
- **Linting (ruff)**: A, B, C4, E, W, ERA, F, I, N, PT, Q, S, SIM, UP

## Common Development Commands

```bash
make all      # Full check: lint, mypy, test, build
make test     # Run tests
make lint     # Run all linters
make mypy     # Type check
make help     # Show all available targets
./calc        # Run calculator (interactive)
```

## Documentation Maintenance

The project maintains feature documentation in multiple places with specific roles:

- **Help command** (`src/calc/help_text.py`): Quick reference for users during calculator use - minimal content only
- **README.md**: Detailed user documentation with examples for all features
- **CLAUDE.md**: Architecture, development commands, and implementation details for AI/developers
