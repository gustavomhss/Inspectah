from __future__ import annotations
import ast
import re
from typing import Any, Callable, Dict, List, Optional


ALLOWED_FUNCTIONS = {
    "min": min,
    "max": max,
    "abs": abs,
    "round": round,
}


def concat(*values: Any) -> str:
    return "".join("" if value is None else str(value) for value in values)


def length(value: Any) -> int:
    if value is None:
        return 0
    return len(value)  # type: ignore[arg-type]


def coalesce(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def if_expr(condition: Any, when_true: Any, when_false: Any) -> Any:
    return when_true if condition else when_false


def lag(field_name: str, *, history: Optional[List[Dict[str, Any]]], offset: int = 1) -> Any:
    if not history:
        raise ValueError("lag requires history")
    if offset < 1 or offset > len(history):
        return None
    return history[offset - 1].get(field_name)


SAFE_FUNCTIONS: Dict[str, Callable[..., Any]] = {
    "concat": concat,
    "coalesce": coalesce,
    "_iel_if": if_expr,
    "length": length,
}


class IELVisitor(ast.NodeVisitor):
    allowed_nodes = {
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.BoolOp,
        ast.Compare,
        ast.Call,
        ast.Load,
        ast.Name,
        ast.Constant,
        ast.IfExp,
        ast.Subscript,
        ast.Index,
        ast.Attribute,
        ast.List,
        ast.Tuple,
        ast.Dict,
        ast.keyword,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.BitXor,
        ast.USub,
        ast.Not,
        ast.And,
        ast.Or,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.Gt,
        ast.LtE,
        ast.GtE,
        ast.Is,
        ast.IsNot,
    }

    allowed_ops = {
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.BitXor,
        ast.USub,
        ast.Not,
        ast.And,
        ast.Or,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.Gt,
        ast.LtE,
        ast.GtE,
        ast.Is,
        ast.IsNot,
    }

    def __init__(self, allowed_names: List[str]) -> None:
        self.allowed_names = set(allowed_names)

    def generic_visit(self, node: ast.AST) -> None:
        if type(node) not in self.allowed_nodes:
            raise ValueError(f"IEL expression contains unsupported node: {type(node).__name__}")
        super().generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        else:
            raise ValueError("IEL disallows attribute-based function calls")
        if func_name not in SAFE_IDENTIFIERS:
            raise ValueError(f"IEL disallows function {func_name}")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id not in self.allowed_names and node.id not in SAFE_IDENTIFIERS:
            raise ValueError(f"IEL disallows identifier {node.id}")

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if type(node.op) not in self.allowed_ops:
            raise ValueError(f"IEL disallows operator {type(node.op).__name__}")
        self.generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if type(node.op) not in self.allowed_ops:
            raise ValueError(f"IEL disallows unary operator {type(node.op).__name__}")
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        if type(node.op) not in self.allowed_ops:
            raise ValueError(f"IEL disallows boolean operator {type(node.op).__name__}")
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        for op in node.ops:
            if type(op) not in self.allowed_ops:
                raise ValueError(f"IEL disallows comparator {type(op).__name__}")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        raise ValueError("IEL disallows attribute access")


_IF_PATTERN = re.compile(r"\bif\s*\(")


def _rewrite_expression(expression: str) -> str:
    return _IF_PATTERN.sub("_iel_if(", expression)


SAFE_IDENTIFIERS = set(ALLOWED_FUNCTIONS.keys()) | set(SAFE_FUNCTIONS.keys()) | {"lag"}


def validate_expression(expression: str, allowed_variables: Optional[List[str]] = None) -> None:
    allowed = allowed_variables or []
    expression = _rewrite_expression(expression)
    tree = ast.parse(expression, mode="eval")
    IELVisitor(allowed).visit(tree)


def evaluate_expression(
    expression: str,
    variables: Dict[str, Any],
    *,
    history: Optional[List[Dict[str, Any]]] = None,
) -> Any:
    allowed_names = list(variables.keys())
    expression = _rewrite_expression(expression)
    validate_expression(expression, allowed_names)
    env: Dict[str, Any] = {name: variables.get(name) for name in allowed_names}
    env.update(ALLOWED_FUNCTIONS)
    env.update(SAFE_FUNCTIONS)

    def lag_wrapper(field_name: str, offset: int = 1):
        return lag(field_name, history=history, offset=offset)

    env["lag"] = lag_wrapper
    compiled = compile(expression, "<iel>", "eval")
    return eval(compiled, {"__builtins__": {}}, env)


__all__ = ["evaluate_expression", "validate_expression"]
