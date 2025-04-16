from pathlib import Path
from typing import cast

from lark import Lark, Tree

from .ast import RAExpression, Relation
from .transformer import RATransformer


grammar_path = Path(__file__).parent / 'grammar.lark'

with grammar_path.open() as f:
    grammar = f.read()

parser = Lark(
    grammar,
    start='expr',
    parser='lalr',
    propagate_positions=True,
    cache=True,
    tree_class=Tree[Relation],
)


def parse_ra(ra_text: str) -> RAExpression:
    parse_tree = cast(Tree[Relation], parser.parse(ra_text))
    print(parse_tree.pretty())
    return RATransformer().transform(parse_tree)
