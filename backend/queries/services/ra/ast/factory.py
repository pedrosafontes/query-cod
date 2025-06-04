from collections.abc import Callable
from typing import TYPE_CHECKING, Union

from .attribute import Attribute


if TYPE_CHECKING:
    from .query import RAQuery


def attribute(attr: str | Attribute) -> Attribute:
    if isinstance(attr, str):
        if '.' in attr:
            relation, name = attr.split('.', 1)
            return Attribute(name=name, relation=relation)
        else:
            return Attribute(name=attr)
    return attr


def query(relation: Union['RAQuery', str]) -> 'RAQuery':
    from .query import Relation

    if isinstance(relation, str):
        return Relation(name=relation)
    return relation


def cartesian(relations: list['RAQuery']) -> 'RAQuery':
    return _combine_relations(relations, lambda left, right: left.cartesian(right))


def natural_join(relations: list['RAQuery']) -> 'RAQuery':
    return _combine_relations(relations, lambda left, right: left.natural_join(right))


def anti_join(relations: list['RAQuery']) -> 'RAQuery':
    return _combine_relations(relations, lambda left, right: left.anti_join(right))


def _combine_relations(
    relations: list['RAQuery'], operator: Callable[['RAQuery', 'RAQuery'], 'RAQuery']
) -> 'RAQuery':
    if not relations:
        raise ValueError('No relations provided for combination')
    if len(relations) == 1:
        return relations[0]
    result = relations[0]
    for relation in relations[1:]:
        result = operator(result, relation)
    return result


def unnest_cartesian_operands(query: 'RAQuery') -> list['RAQuery']:
    from .query import SetOperator, SetOperatorKind

    match query:
        case SetOperator(operator=SetOperatorKind.CARTESIAN):
            return unnest_cartesian_operands(query.left) + unnest_cartesian_operands(query.right)
        case _:
            return [query]
