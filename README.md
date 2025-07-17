# calc

A simple command-line calculator

## Quick Start

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/shakiyam/calc.git
    cd calc
    ```

2.  **Run it:**
    Use the `./calc` script to start the interactive shell. It requires Docker or Podman and will pull the necessary image automatically.

    ```bash
    $ ./calc
    1 + 1
    = 2
    1 + ? x 3,000
    = 6,001
    00:01:00 + 123sec
    = 00:03:03
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
| `tan(n)`        | Tangent of `n` (in radians)                     |

When using functions with multiple arguments (e.g., `max(a, b, ...)`), ensure there is a space after the comma separating the arguments.

### Constants

| Constant | Description      |
| :------- | :--------------- |
| `pi`     | 3.1415926535...  |
| `e`      | 2.7182818284...  |

### Time Calculations

`calc` supports time calculations. You can input time in `HH:MM:SS` format or as seconds with the `sec` or `s` unit. The output is formatted as `[D day[s], ]HH:MM:SS[.UUUUUU]`.

### History

When running in the interactive shell (as shown in the Quick Start), you can access the previous result with the `?` symbol.

### Number Formatting

Numbers are displayed with a comma as a thousands separator (e.g., `1,234,567`). Input also supports numbers with thousands separators.

### Exiting

Type `exit` to leave the interactive shell.

## Detailed Usage

### Containerized Execution (Recommended)

The `./calc` script runs the calculator inside a container.

-   **Interactive Shell Mode:**
    ```bash
    ./calc
    ```
-   **Direct Command Execution:**
    Pass the expression as a single argument.
    ```bash
    ./calc '1 + 2 * 3,000'
    ```

### Local Python Execution

This method is for users who prefer not to use containers.

-   **Setup:** From the project root directory (where this README.md is located), install the package and its dependencies using [`uv`](https://docs.astral.sh/uv/).
    
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

-   **Usage:** After installation, run the calculator from anywhere:
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
