from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    Attribute,
    Comparison,
    ComparisonOperator,
    RAExpression,
    Relation,
    Selection,
)


@pytest.mark.parametrize(
    'query',
    [
        Selection(Comparison(ComparisonOperator.GREATER_THAN, Attribute('A'), 10), Relation('R')),
    ],
)
def test_valid_selection(query: RAExpression, assert_valid: Callable[[RAExpression], None]) -> None:
    assert_valid(query)
