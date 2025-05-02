import pytest
from queries.services.types import RelationalSchema

from .conftest import assert_valid


@pytest.mark.parametrize(
    'query',
    [
        "SELECT DATE '2025-04-29'",
        "SELECT TIME '14:30:00'",
        "SELECT TIMESTAMP '2025-04-29 14:30:00'",
        "SELECT DATE '1999-12-31'",
        "SELECT TIME '23:59:59.999'",
        "SELECT TIMESTAMP '2000-01-01 00:00:00.000'",
        'SELECT CURRENT_DATE',
        'SELECT CURRENT_TIME',
        'SELECT CURRENT_TIMESTAMP',
    ],
)
def test_valid_literals(query: str, schema: RelationalSchema) -> None:
    assert_valid(query, schema)
