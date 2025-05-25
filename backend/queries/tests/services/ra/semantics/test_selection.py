from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    GT,
    RAQuery,
    Relation,
    attribute,
)


@pytest.mark.parametrize(
    'query',
    [
        Relation('R').select(GT(attribute('A'), 10)),
    ],
)
def test_valid_selection(query: RAQuery, assert_valid: Callable[[RAQuery], None]) -> None:
    assert_valid(query)
