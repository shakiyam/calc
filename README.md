calc
====

A simple command-line calculator

Usage
-----

You can use calc in two ways: shell mode and command.

### Shell mode ###

```
$ python3 calc.py
1 + 1
= 2
1 + ? x 3,000
= 6,001

$
```

### Command ###

```
$ python3 calc.py '1 + 2 x 3,000'
= 6,001
$
```

Supported operators, functions, etc.
------------------------------------

### Operators ###

`+`, `-`, `*`, `x`, `X`, `/`, `%`, `^`, `**`

`x` and `X` are aliases for `*` and `^` is an alias for `**`.

### Functions ###

* `ceil(n)` return the ceiling of n, the smallest integer greater than or equal to n.
* `floor(n)` return the floor of n, the largest integer less than or equal to n.
* `round(n[@d])` return n rounded to d precision after the decimal point. If d is omitted, it returns the nearest integer to its input.

### Units ###

* `sec` or `s` convert seconds to [D day[s], ]HH:MM:SS[.UUUUUU].

### History ###

Previous results can be accessed with the `?` symbol.

Author
------

[Shinichi Akiyama](https://github.com/shakiyam)

License
-------

[MIT License](https://opensource.org/licenses/mit)
