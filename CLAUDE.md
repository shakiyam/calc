# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Key Features

- Comment support (`#`)
- Operator aliases (`＋`, `－`, `×`, `x`, `X`, `÷`, `^`)
- Time calculations with English/Japanese natural language support
- Time output formats (`as <format>` directive, `format` session command)
- Interactive shell with history (`?` for previous result)
- Number formatting with thousands separators
- Unit handling (non-time units like `個`, `円`, `kg` are ignored)
- Help command (`help`)

## Project Structure

```text
calc/
├── src/calc/              # Main source code
│   ├── __init__.py        # Package marker (empty)
│   ├── __main__.py        # Entry point, expression parsing, shell
│   ├── evaluator.py       # Safe AST-based expression evaluation
│   ├── time_utils.py      # Time expression utilities
│   ├── help_text.py       # Help command text
│   └── py.typed           # PEP 561 marker
├── tests/                 # Test files
│   ├── test_basic.py      # Arithmetic, comments, formatting, history
│   ├── test_functions.py  # Math functions and constants
│   ├── test_output_format.py # Time output formats (as directive, format command)
│   ├── test_time.py       # Time calculations
│   ├── test_time_utils.py # Time utilities
│   └── test_errors.py     # Error handling
├── tools/                 # Build and lint scripts
├── .github/               # GitHub Actions workflows
├── Dockerfile             # Production image
├── Dockerfile.dev         # Development image
├── Makefile               # Build automation
├── calc                   # Launcher script (runs the production image)
├── calc_dev               # Dev launcher (runs pytest/mypy in the dev image)
└── pyproject.toml         # Project configuration
```

## Architecture

Python-based command-line calculator with secure expression evaluation using AST (Abstract Syntax Tree) parsing.

**Processing Pipeline**:

1. `src/calc/__main__.py`: Parse comments, extract the trailing `as <format>` directive,
   handle `?` substitution, convert time formats
2. `src/calc/evaluator.py`: Parse to AST and evaluate with security restrictions
3. `src/calc/__main__.py`: Format output (thousands separators, time formatting per the
   `as` directive or the session default set by the `format` command)

**Security Model**: The evaluator uses a whitelist approach:

- `_ALLOWED_BINARY_OPERATORS`: Only basic math operators (+, -, *, /, %, **);
  unary +/- are handled separately in `_eval_node`
- `_ALLOWED_FUNCTIONS`: Math, rounding, and aggregate functions, timedelta
- `_ALLOWED_CONSTANTS`: Just pi and e

Never add functions that could execute arbitrary code or access the filesystem.

**Round-trip Invariant**: History reuse (`?`) substitutes the formatted output string
into the next expression, so every time output format must re-parse as valid input.
When adding or changing output formats, emit only text the input grammar in
`time_utils.py` accepts (e.g. unit formats keep the unit word: `90 min`, never a bare
`90`), and extend the input patterns if a new output shape needs them.

## Code Style

- **Python**: 3.10+ with type hints required (mypy strict mode)
- **Line Length**: 100 characters
- **Linting (ruff)**: A, B, C4, E, W, ERA, F, I, N, PT, Q, S, SIM, UP

## Common Development Commands

```bash
make all      # Check for updates, format, lint, update requirements, mypy, test, and build
make test     # Run tests
make format   # Format Python code and shell scripts
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
