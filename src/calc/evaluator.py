import ast
import math
import operator as op
from datetime import timedelta
from decimal import Decimal
from typing import Any, Callable, Dict, Final, Union

_ALLOWED_BINARY_OPERATORS: Final[Dict[type, Callable[[Any, Any], Any]]] = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
}


def _validate_uniform_types(
    args: tuple[Union[Decimal, timedelta], ...], function_name: str
) -> type:
    """Validate that all arguments are of the same type"""
    if not args:
        raise TypeError(f'{function_name} expected at least 1 argument, got 0')

    expected_type = type(args[0])

    for arg in args:
        if not isinstance(arg, expected_type):
            raise TypeError(f'Cannot mix timedelta and Decimal in {function_name}')

    return expected_type


def _ensure_decimal(value: Union[Decimal, timedelta]) -> Decimal:
    """Ensure value is Decimal, raising TypeError for timedelta"""
    if isinstance(value, Decimal):
        return value
    else:
        raise TypeError(f'Math functions only accept Decimal values, got {type(value).__name__}')


def _apply_to_timedelta_seconds(td: timedelta, func: Callable[..., Any], *args: Any) -> timedelta:
    """Apply function to timedelta by converting to seconds and back"""
    seconds = Decimal(str(td.total_seconds()))
    result_seconds = func(seconds, *args)
    return timedelta(seconds=float(result_seconds))


def _avg_wrapper(*args: Union[Decimal, timedelta]) -> Union[Decimal, timedelta]:
    """Calculate average of Decimal or timedelta values"""
    arg_type = _validate_uniform_types(args, 'avg')

    if arg_type is timedelta:
        total_time = sum(args, timedelta())
        assert isinstance(total_time, timedelta)
        avg_seconds = total_time.total_seconds() / len(args)
        return timedelta(seconds=avg_seconds)
    else:
        total = sum(args, Decimal('0'))
        assert isinstance(total, Decimal)
        return total / Decimal(len(args))


def _max_wrapper(*args: Union[Decimal, timedelta]) -> Union[Decimal, timedelta]:
    """Return maximum of Decimal or timedelta values"""
    if len(args) == 1:
        return args[0]
    _validate_uniform_types(args, 'max')
    return max(*args)


def _min_wrapper(*args: Union[Decimal, timedelta]) -> Union[Decimal, timedelta]:
    """Return minimum of Decimal or timedelta values"""
    if len(args) == 1:
        return args[0]
    _validate_uniform_types(args, 'min')
    return min(*args)


def _sum_wrapper(*args: Union[Decimal, timedelta]) -> Union[Decimal, timedelta]:
    """Calculate sum of Decimal or timedelta values"""
    if not args:
        return Decimal('0')

    arg_type = _validate_uniform_types(args, 'sum')

    if arg_type is timedelta:
        return sum(args, timedelta())
    else:
        return sum(args, Decimal('0'))


_ALLOWED_FUNCTIONS: Final[Dict[str, Callable[..., Any]]] = {
    'abs': abs,
    'avg': _avg_wrapper,
    'ceil': math.ceil,
    'cos': math.cos,
    'exp': math.exp,
    'floor': math.floor,
    'log': math.log,
    'max': _max_wrapper,
    'min': _min_wrapper,
    'round': round,
    'sin': math.sin,
    'sqrt': math.sqrt,
    'sum': _sum_wrapper,
    'tan': math.tan,
    'timedelta': timedelta,
}

_ALLOWED_CONSTANTS: Final[Dict[str, Decimal]] = {
    'e': Decimal(str(math.e)),
    'pi': Decimal(str(math.pi)),
}


def _can_mix_types(
    left: Union[Decimal, timedelta],
    right: Union[Decimal, timedelta],
    operator_type: type
) -> bool:
    """Check if type mixing is allowed for the given operation"""
    if isinstance(left, timedelta) and isinstance(right, Decimal):
        return operator_type in [ast.Mult, ast.Div]
    elif isinstance(left, Decimal) and isinstance(right, timedelta):
        return operator_type == ast.Mult
    else:
        return True


def _convert_for_mixed_operation(
    left: Union[Decimal, timedelta],
    right: Union[Decimal, timedelta]
) -> tuple[Union[Decimal, float, timedelta], Union[Decimal, float, timedelta]]:
    """Convert operands for mixed-type operations"""
    if isinstance(left, timedelta) and isinstance(right, Decimal):
        return left, float(right)
    elif isinstance(left, Decimal) and isinstance(right, timedelta):
        return float(left), right
    else:
        return left, right


def _eval_binop(
    left: Union[Decimal, timedelta],
    right: Union[Decimal, timedelta],
    operator_type: type
) -> Union[Decimal, timedelta]:
    """Evaluate binary operation with type mixing rules for timedelta and Decimal"""
    if operator_type not in _ALLOWED_BINARY_OPERATORS:
        raise TypeError(f'Unsupported operator: {operator_type.__name__}')

    if not _can_mix_types(left, right, operator_type):
        op_name = operator_type.__name__.replace('ast.', '')
        left_type = type(left).__name__
        right_type = type(right).__name__
        raise TypeError(
            f"Unsupported operation '{op_name}' between {left_type} and {right_type}"
        )

    operator_func = _ALLOWED_BINARY_OPERATORS[operator_type]
    converted_left, converted_right = _convert_for_mixed_operation(left, right)
    result = operator_func(converted_left, converted_right)
    assert isinstance(result, (Decimal, timedelta))
    return result


def _eval_math_func(
    func_name: str,
    args: list[Union[Decimal, timedelta]],
    kwargs: dict[str, Union[Decimal, timedelta]]
) -> Decimal:
    """Evaluate math functions (cos, exp, log, sin, sqrt, tan)"""
    float_args = [float(_ensure_decimal(arg)) for arg in args]
    float_kwargs = {k: float(_ensure_decimal(v)) for k, v in kwargs.items()}
    result = _ALLOWED_FUNCTIONS[func_name](*float_args, **float_kwargs)
    return Decimal(str(result))


def _eval_rounding_func(
    func_name: str, args: list[Union[Decimal, timedelta]]
) -> Union[Decimal, timedelta]:
    """Evaluate rounding functions (ceil, floor, round)"""
    if isinstance(args[0], timedelta):
        if func_name == 'round' and len(args) > 1:
            precision = int(_ensure_decimal(args[1]))
            return _apply_to_timedelta_seconds(args[0], round, precision)
        else:
            return _apply_to_timedelta_seconds(args[0], _ALLOWED_FUNCTIONS[func_name])
    else:
        decimal_arg = _ensure_decimal(args[0])
        if func_name == 'round' and len(args) > 1:
            precision = int(_ensure_decimal(args[1]))
            return round(decimal_arg, precision)
        else:
            result = _ALLOWED_FUNCTIONS[func_name](decimal_arg)
            return Decimal(str(result))


def _eval_timedelta(
    args: list[Union[Decimal, timedelta]],
    kwargs: dict[str, Union[Decimal, timedelta]]
) -> timedelta:
    """Evaluate timedelta function"""
    float_args = [float(_ensure_decimal(arg)) for arg in args]
    float_kwargs = {k: float(_ensure_decimal(v)) for k, v in kwargs.items()}
    return timedelta(*float_args, **float_kwargs)


def _eval_func(
    func_name: str,
    args: list[Union[Decimal, timedelta]],
    kwargs: dict[str, Union[Decimal, timedelta]]
) -> Union[Decimal, timedelta]:
    """Dispatch function call to appropriate handler"""
    if func_name not in _ALLOWED_FUNCTIONS:
        raise TypeError(f'Unsupported function: {func_name}')

    if func_name in ['cos', 'exp', 'log', 'sin', 'sqrt', 'tan']:
        return _eval_math_func(func_name, args, kwargs)
    elif func_name in ['ceil', 'floor', 'round']:
        return _eval_rounding_func(func_name, args)
    elif func_name == 'timedelta':
        return _eval_timedelta(args, kwargs)
    else:
        result = _ALLOWED_FUNCTIONS[func_name](*args, **kwargs)
        assert isinstance(result, (Decimal, timedelta))
        return result


def _eval_node(node: ast.AST, expression: str) -> Union[Decimal, timedelta]:
    """Recursively evaluate AST node to Decimal or timedelta"""
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float)):
            raise TypeError(f'Unsupported constant type: {type(node.value).__name__}')
        original_str = expression[node.col_offset:node.end_col_offset]
        return Decimal(original_str)
    elif isinstance(node, ast.BinOp):
        left = _eval_node(node.left, expression)
        right = _eval_node(node.right, expression)
        return _eval_binop(left, right, type(node.op))
    elif isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.UAdd):
            return _eval_node(node.operand, expression)
        elif isinstance(node.op, ast.USub):
            return -_eval_node(node.operand, expression)
        else:
            raise TypeError(f'Unsupported unary operator: {type(node.op).__name__}')
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise TypeError(f'Unsupported function call type: {type(node.func).__name__}')
        func_name = node.func.id
        args = [_eval_node(arg, expression) for arg in node.args]
        kwargs = {}
        for keyword in node.keywords:
            if keyword.arg is not None:
                kwargs[keyword.arg] = _eval_node(keyword.value, expression)
        return _eval_func(func_name, args, kwargs)
    elif isinstance(node, ast.Name):
        if node.id in _ALLOWED_CONSTANTS:
            return _ALLOWED_CONSTANTS[node.id]
        raise TypeError(f'Unsupported name: {node.id}')
    else:
        raise TypeError(f'Unsupported AST node type: {type(node).__name__}')


def safe_eval(expression: str) -> Union[Decimal, timedelta]:
    """Safely evaluate mathematical expression using AST-based whitelist approach"""
    node = ast.parse(expression, mode='eval').body
    return _eval_node(node, expression)
