from .ra.parser.ast import RAExpression
from .ra.tree.converter import RATreeConverter
from .ra.tree.types import RATree
from .types import QueryAST


def transform_ast(ast: QueryAST) -> RATree | None:
    match ast:
        case RAExpression():
            return RATreeConverter().convert(ast)
        case _:
            return None
