import ast
import math
import operator as op
from datetime import timedelta
from decimal import Decimal
from typing import Any, Callable, Dict, Union

allowed_operators: Dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
}


def _min_wrapper(*args: Any) -> Any:
    if len(args) == 1:
        return args[0]
    return min(*args)


def _max_wrapper(*args: Any) -> Any:
    if len(args) == 1:
        return args[0]
    return max(*args)


def _sum_wrapper(*args: Any) -> Any:
    if len(args) == 1:
        return args[0]
    return sum(args)


allowed_functions: Dict[str, Callable[..., Any]] = {
    'abs': abs,
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

allowed_constants: Dict[str, Decimal] = {
    'e': Decimal(str(math.e)),
    'pi': Decimal(str(math.pi)),
}


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
        if type(node.op) not in allowed_operators:
            raise TypeError(f'Unsupported operator: {type(node.op).__name__}')
        left = eval_expr(node.left, expression)
        right = eval_expr(node.right, expression)

        if isinstance(left, timedelta) and isinstance(right, Decimal):
            right = float(right)  # type: ignore
        elif isinstance(right, timedelta) and isinstance(left, Decimal):
            left = float(left)  # type: ignore

        return allowed_operators[type(node.op)](left, right)
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
        if func_name not in allowed_functions:
            raise TypeError(f'Unsupported function: {func_name}')
        args = [eval_expr(arg, expression) for arg in node.args]
        kwargs = {}
        for keyword in node.keywords:
            if keyword.arg is not None:
                kwargs[keyword.arg] = eval_expr(keyword.value, expression)

        if func_name in ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt']:
            float_args = [float(arg) for arg in args]  # type: ignore
            float_kwargs = {k: float(v) for k, v in kwargs.items()}  # type: ignore
            result = allowed_functions[func_name](*float_args, **float_kwargs)
            return Decimal(str(result))
        elif func_name in ['ceil', 'floor']:
            result = allowed_functions[func_name](args[0])
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
            return allowed_functions[func_name](*float_args, **float_kwargs)
        else:
            return allowed_functions[func_name](*args, **kwargs)
    elif isinstance(node, ast.Name):
        if node.id in allowed_constants:
            return allowed_constants[node.id]
        raise TypeError(f'Unsupported name: {node.id}')
    else:
        raise TypeError(f'Unsupported AST node type: {type(node).__name__}')


def safe_eval(expression: str) -> Any:
    """
    Safely evaluate a mathematical expression string.
    """
    node = ast.parse(expression, mode='eval').body
    return eval_expr(node, expression)
