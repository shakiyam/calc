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


def _validate_uniform_types(args: tuple, function_name: str) -> type:
    """Validate that all arguments are of the same type"""
    if not args:
        raise TypeError(f'{function_name} expected at least 1 argument, got 0')

    expected_type = type(args[0])

    for arg in args:
        if not isinstance(arg, expected_type):
            raise TypeError(f'Cannot mix timedelta and Decimal in {function_name}')

    return expected_type


def _min_wrapper(*args: Union[Decimal, timedelta]) -> Union[Decimal, timedelta]:
    if len(args) == 1:
        return args[0]
    _validate_uniform_types(args, 'min')
    return min(*args)


def _max_wrapper(*args: Union[Decimal, timedelta]) -> Union[Decimal, timedelta]:
    if len(args) == 1:
        return args[0]
    _validate_uniform_types(args, 'max')
    return max(*args)


def _sum_wrapper(*args: Union[Decimal, timedelta]) -> Union[Decimal, timedelta]:
    if not args:
        return Decimal('0')

    arg_type = _validate_uniform_types(args, 'sum')

    if arg_type is timedelta:
        return sum(args, timedelta())
    else:
        return sum(args, Decimal('0'))


def _avg_wrapper(*args: Union[Decimal, timedelta]) -> Union[Decimal, timedelta]:
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


def _ensure_decimal(value: Union[Decimal, timedelta]) -> Decimal:
    if isinstance(value, Decimal):
        return value
    else:
        raise TypeError(f'Math functions only accept Decimal values, got {type(value).__name__}')


def _math_function_wrapper(
    func: Callable[[float], float], *args: Decimal, **kwargs: Decimal
) -> Decimal:
    float_args = [float(arg) for arg in args]
    float_kwargs = {k: float(v) for k, v in kwargs.items()}
    result = func(*float_args, **float_kwargs)
    return Decimal(str(result))


def _eval_binop(
    left: Union[Decimal, timedelta],
    right: Union[Decimal, timedelta],
    operator_type: type
) -> Union[Decimal, timedelta]:
    if operator_type not in _ALLOWED_BINARY_OPERATORS:
        raise TypeError(f'Unsupported operator: {operator_type.__name__}')

    operator_func = _ALLOWED_BINARY_OPERATORS[operator_type]

    if isinstance(left, type(right)) and isinstance(right, type(left)):
        return operator_func(left, right)

    if isinstance(left, timedelta) and isinstance(right, Decimal):
        if operator_type in [ast.Mult, ast.Div]:
            converted_right: float = float(right)
            result: timedelta = operator_func(left, converted_right)
            return result
        else:
            op_name = operator_type.__name__.replace('ast.', '')
            raise TypeError(
                f"Unsupported operation '{op_name}' between timedelta and Decimal. "
                f'Only multiplication and division are allowed.'
            )

    elif isinstance(left, Decimal) and isinstance(right, timedelta):
        if operator_type == ast.Mult:
            converted_left: float = float(left)
            result = operator_func(converted_left, right)
            return result
        else:
            op_name = operator_type.__name__.replace('ast.', '')
            raise TypeError(
                f"Unsupported operation '{op_name}' between Decimal and timedelta. "
                f'Only multiplication is allowed in this order.'
            )

    return operator_func(left, right)


def _eval_func(func_name: str, args: list, kwargs: dict) -> Union[Decimal, timedelta]:
    if func_name not in _ALLOWED_FUNCTIONS:
        raise TypeError(f'Unsupported function: {func_name}')

    if func_name in ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt']:
        decimal_args = [_ensure_decimal(arg) for arg in args]
        decimal_kwargs = {k: _ensure_decimal(v) for k, v in kwargs.items()}
        return _math_function_wrapper(
            _ALLOWED_FUNCTIONS[func_name], *decimal_args, **decimal_kwargs
        )
    elif func_name in ['ceil', 'floor']:
        if isinstance(args[0], timedelta):
            seconds = Decimal(str(args[0].total_seconds()))
            result_seconds = _ALLOWED_FUNCTIONS[func_name](seconds)
            return timedelta(seconds=float(result_seconds))
        else:
            decimal_arg = _ensure_decimal(args[0])
            result = _ALLOWED_FUNCTIONS[func_name](decimal_arg)
            return Decimal(str(result))
    elif func_name == 'round':
        if isinstance(args[0], timedelta):
            seconds = Decimal(str(args[0].total_seconds()))
            if len(args) == 1:
                result_seconds = round(seconds)
            else:
                precision = int(_ensure_decimal(args[1]))
                result_seconds = round(seconds, precision)
            return timedelta(seconds=float(result_seconds))
        else:
            decimal_arg = _ensure_decimal(args[0])
            if len(args) == 1:
                return Decimal(str(round(decimal_arg)))
            else:
                precision = int(_ensure_decimal(args[1]))
                return round(decimal_arg, precision)
    elif func_name == 'timedelta':
        decimal_args = [_ensure_decimal(arg) for arg in args]
        decimal_kwargs = {k: _ensure_decimal(v) for k, v in kwargs.items()}
        float_args = [float(arg) for arg in decimal_args]
        float_kwargs = {k: float(v) for k, v in decimal_kwargs.items()}
        return _ALLOWED_FUNCTIONS[func_name](*float_args, **float_kwargs)
    else:
        return _ALLOWED_FUNCTIONS[func_name](*args, **kwargs)


def _eval_expr(node: ast.AST, expression: str) -> Union[Decimal, timedelta]:
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float)):
            raise TypeError(f'Unsupported constant type: {type(node.value).__name__}')
        original_str = expression[node.col_offset:node.end_col_offset]
        return Decimal(original_str)
    elif isinstance(node, ast.BinOp):
        left = _eval_expr(node.left, expression)
        right = _eval_expr(node.right, expression)
        return _eval_binop(left, right, type(node.op))
    elif isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.UAdd):
            return _eval_expr(node.operand, expression)
        elif isinstance(node.op, ast.USub):
            return -_eval_expr(node.operand, expression)
        else:
            raise TypeError(f'Unsupported unary operator: {type(node.op).__name__}')
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise TypeError(f'Unsupported function call type: {type(node.func).__name__}')
        func_name = node.func.id
        args = [_eval_expr(arg, expression) for arg in node.args]
        kwargs = {}
        for keyword in node.keywords:
            if keyword.arg is not None:
                kwargs[keyword.arg] = _eval_expr(keyword.value, expression)
        return _eval_func(func_name, args, kwargs)
    elif isinstance(node, ast.Name):
        if node.id in _ALLOWED_CONSTANTS:
            return _ALLOWED_CONSTANTS[node.id]
        raise TypeError(f'Unsupported name: {node.id}')
    else:
        raise TypeError(f'Unsupported AST node type: {type(node).__name__}')


def safe_eval(expression: str) -> Union[Decimal, timedelta]:
    node = ast.parse(expression, mode='eval').body
    return _eval_expr(node, expression)
