# calc

A simple command-line calculator

## Quick Start

1. **Clone the repository:**

    ```bash
    git clone https://github.com/shakiyam/calc.git
    cd calc
    ```

2. **Run it:** Use the `./calc` script to start the interactive shell. It requires Docker or Podman and will pull the necessary image automatically.

   *Note: If you prefer not to use Docker/Podman, see the [Local Python Execution](#local-python-execution) section below.*

    ```bash
    $ ./calc
    1 + 1
    = 2
    1 + ? x 3,000
    = 6,001
    00:01:00 + 123sec
    = 00:03:03
    25:00:00
    = 1 day and 01:00:00
    exit
    $
    ```

## Features

### Comments

Comments start with `#` and extend to the end of the line.
`1 + 1 # This is a comment`

### Operators

| Operator | Description      | Aliases    |
| :------- | :--------------- | :--------- |
| `+`      | Addition         |            |
| `-`      | Subtraction      |            |
| `*`      | Multiplication   | `x`, `X`   |
| `/`      | Division         |            |
| `%`      | Modulo           |            |
| `**`     | Exponentiation   | `^`        |

### Functions

| Function        | Description                                     |
| :-------------- | :---------------------------------------------- |
| `abs(n)`        | Absolute value of `n`                           |
| `avg(a, b, ...)`| Average of all arguments                        |
| `ceil(n)`       | Ceiling: smallest integer >= n                  |
| `cos(n)`        | Cosine of `n` (in radians)                      |
| `exp(n)`        | Exponential of `n` (e**n)                       |
| `floor(n)`      | Floor: largest integer <= n                     |
| `log(n)`        | Natural logarithm of `n`                        |
| `max(a, b, ...)`| Maximum of all arguments                        |
| `min(a, b, ...)`| Minimum of all arguments                        |
| `round(n[, d])` | Rounds `n` to `d` decimal places (default is 0) |
| `sin(n)`        | Sine of `n` (in radians)                        |
| `sqrt(n)`       | Square root of `n`                              |
| `sum(a, b, ...)`| Sum of all arguments                            |
| `tan(n)`        | Tangent of `n` (in radians)                     |

**Important:** When using functions with multiple arguments, include a space after each comma:

- ✅ Correct: `max(1, 2, 3)` or `avg(10, 20, 30)`
- ❌ Incorrect: `max(1,2,3)` or `avg(10,20,30)`

### Constants

| Constant | Description      |
| :------- | :--------------- |
| `pi`     | 3.1415926535...  |
| `e`      | 2.7182818284...  |

### Time Calculations

`calc` supports comprehensive time calculations with natural language input:

- **Output:** Always uses `HH:MM:SS` format with `and` for days: `1 day and 02:00:00` (microseconds shown when present)

**Input format examples:**

```text
# Basic formats
01:30:45                    → 01:30:45
00:01:30.500000             → 00:01:30.500000
60s                         → 00:01:00
30min                       → 00:30:00
5hr                         → 05:00:00
1 day                       → 1 day and 00:00:00
2d                          → 2 days and 00:00:00

# Compact combinations
1h 30m                      → 01:30:00
1m 5s                       → 00:01:05

# Day and combinations
1 day and 10 hours          → 1 day and 10:00:00
1 day and 1 hour 2 min      → 1 day and 01:02:00

# Natural language
1 day 2 hours 30 minutes    → 1 day and 02:30:00
2 hours and 30 minutes      → 02:30:00
```

**Calculation examples:**

```text
00:01:00 + 30s              → 00:01:30
01:00:00 - 30s              → 00:59:30
00:30:00 * 2                → 01:00:00
02:00:00 / 2                → 01:00:00
1h + 30min                  → 01:30:00
30min - 5s                  → 00:29:55
```

### History

When running in the interactive shell (as shown in the Quick Start), you can access the previous result with the `?` symbol.

### Number Formatting

Numbers are displayed with a comma as a thousands separator (e.g., `1,234,567`). Input also supports numbers with thousands separators.

### Exiting

Type `exit` to leave the interactive shell.

## Detailed Usage

### Containerized Execution (Recommended)

The `./calc` script runs the calculator inside a container.

- **Interactive Shell Mode:**

  ```bash
  ./calc
  ```

- **Direct Command Execution:** Pass the expression as a single argument.

  ```bash
  ./calc '1 + 2 * 3,000'
  ```

### Local Python Execution

This method is for users who prefer not to use containers.

- **Setup:** From the project root directory (where this README.md is located), install the package and its dependencies using [`uv`](https://docs.astral.sh/uv/).

  Option 1: Using virtual environment (recommended)

  ```bash
  uv venv
  source .venv/bin/activate  # On Windows: .venv\Scripts\activate
  uv pip install -e .
  ```

  Option 2: System-wide installation (may require administrator privileges)

  ```bash
  uv pip install --system -e .
  ```

- **Usage:** After installation, run the calculator from anywhere:

  ```bash
  # Interactive Mode
  calc
  
  # Direct Command
  calc '1 + 2 * 3'
  ```

## Author

[Shinichi Akiyama](https://github.com/shakiyam)

## License

[MIT License](https://opensource.org/licenses/MIT)
