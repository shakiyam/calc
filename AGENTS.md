# AGENTS.md

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
make all         # Run all checks (see `make help` for what it includes)
make test        # Run tests
make format      # Run all formatting
make lint        # Run all linting
make mypy        # Type check
make help        # Show all available targets
./calc           # Run calculator (interactive)
./calc_dev <cmd> # Run a command (e.g. pytest, mypy) in the dev image against the working tree
```

## Documentation Maintenance

The project maintains feature documentation in multiple places with specific roles:

- **Help command** (`src/calc/help_text.py`): Quick reference for users during calculator use - minimal content only
- **README.md**: Detailed user documentation with examples for all features
- **AGENTS.md**: Architecture, development commands, and implementation details for AI/developers

## Decisions

- **Relaxed dive thresholds**: `.dive-ci` raises the limits because dive's default 10% limit on wasted user-layer bytes failed intermittently: the wasted bytes stay at about 5.6MB, but the reported percentage varied (5.6%, 10.7%, 20.5%), leaving little headroom under the 25% limit
