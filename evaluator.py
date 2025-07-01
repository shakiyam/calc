import ast
import math
import operator as op
from datetime import timedelta
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
        return min([args[0]])
    return min(*args)


def _max_wrapper(*args: Any) -> Any:
    if len(args) == 1:
        return max([args[0]])
    return max(*args)


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
    'tan': math.tan,
    'timedelta': timedelta,
}

allowed_constants: Dict[str, float] = {
    'e': math.e,
    'pi': math.pi,
}


def eval_expr(node: ast.AST) -> Union[int, float, timedelta]:
    """
    Recursively evaluate an Abstract Syntax Tree node.
    """
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        if type(node.op) not in allowed_operators:
            raise TypeError(f'Unsupported operator: {type(node.op).__name__}')
        left = eval_expr(node.left)
        right = eval_expr(node.right)
        return allowed_operators[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.UAdd):
            return eval_expr(node.operand)
        elif isinstance(node.op, ast.USub):
            return -eval_expr(node.operand)
        else:
            raise TypeError(f'Unsupported unary operator: {type(node.op).__name__}')
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise TypeError(f'Unsupported function call type: {type(node.func).__name__}')
        func_name = node.func.id
        if func_name not in allowed_functions:
            raise TypeError(f'Unsupported function: {func_name}')
        args = [eval_expr(arg) for arg in node.args]
        kwargs = {}
        for keyword in node.keywords:
            if keyword.arg is not None:
                kwargs[keyword.arg] = eval_expr(keyword.value)
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
    return eval_expr(node)
