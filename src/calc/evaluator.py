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


def _min_wrapper(*args: Union[Decimal, timedelta]) -> Union[Decimal, timedelta]:
    if len(args) == 1:
        return args[0]
    return min(*args)


def _max_wrapper(*args: Union[Decimal, timedelta]) -> Union[Decimal, timedelta]:
    if len(args) == 1:
        return args[0]
    return max(*args)


def _sum_wrapper(*args: Decimal) -> Decimal:
    return sum(args, Decimal('0'))


def _avg_wrapper(*args: Decimal) -> Decimal:
    if len(args) == 0:
        raise TypeError('avg expected at least 1 argument, got 0')
    return sum(args, Decimal('0')) / Decimal(len(args))


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


def eval_binop(
    left: Union[Decimal, timedelta],
    right: Union[Decimal, timedelta],
    operator_type: type
) -> Union[Decimal, timedelta]:
    """
    Evaluate binary operations with type checking for timedelta and Decimal.
    Mixed type operations are restricted to multiplication and division.
    """
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


def eval_expr(node: ast.AST, expression: str) -> Union[Decimal, timedelta]:
    """
    Recursively evaluate an Abstract Syntax Tree node.
    """
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float)):
            raise TypeError(f'Unsupported constant type: {type(node.value).__name__}')
        original_str = expression[node.col_offset:node.end_col_offset]
        return Decimal(original_str)
    elif isinstance(node, ast.BinOp):
        left = eval_expr(node.left, expression)
        right = eval_expr(node.right, expression)
        return eval_binop(left, right, type(node.op))
    elif isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.UAdd):
            return eval_expr(node.operand, expression)
        elif isinstance(node.op, ast.USub):
            return -eval_expr(node.operand, expression)
        else:
            raise TypeError(f'Unsupported unary operator: {type(node.op).__name__}')
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise TypeError(f'Unsupported function call type: {type(node.func).__name__}')
        func_name = node.func.id
        if func_name not in _ALLOWED_FUNCTIONS:
            raise TypeError(f'Unsupported function: {func_name}')
        args = [eval_expr(arg, expression) for arg in node.args]
        kwargs = {}
        for keyword in node.keywords:
            if keyword.arg is not None:
                kwargs[keyword.arg] = eval_expr(keyword.value, expression)
        if func_name in ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt']:
            float_args = [float(arg) for arg in args]  # type: ignore
            float_kwargs = {k: float(v) for k, v in kwargs.items()}  # type: ignore
            result = _ALLOWED_FUNCTIONS[func_name](*float_args, **float_kwargs)
            return Decimal(str(result))
        elif func_name in ['ceil', 'floor']:
            result = _ALLOWED_FUNCTIONS[func_name](args[0])
            return Decimal(str(result))
        elif func_name == 'round':
            if len(args) == 1:
                result = round(args[0])  # type: ignore
                return Decimal(str(result))
            else:
                return round(args[0], int(args[1]))  # type: ignore
        elif func_name == 'timedelta':
            float_args = [float(arg) for arg in args]  # type: ignore
            float_kwargs = {k: float(v) for k, v in kwargs.items()}  # type: ignore
            return _ALLOWED_FUNCTIONS[func_name](*float_args, **float_kwargs)
        else:
            return _ALLOWED_FUNCTIONS[func_name](*args, **kwargs)
    elif isinstance(node, ast.Name):
        if node.id in _ALLOWED_CONSTANTS:
            return _ALLOWED_CONSTANTS[node.id]
        raise TypeError(f'Unsupported name: {node.id}')
    else:
        raise TypeError(f'Unsupported AST node type: {type(node).__name__}')


def safe_eval(expression: str) -> Union[Decimal, timedelta]:
    """
    Safely evaluate a mathematical expression string.
    """
    node = ast.parse(expression, mode='eval').body
    return eval_expr(node, expression)
