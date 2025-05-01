import pytest
from queries.services.sql.semantics.errors import (
    AggregateInWhereError,
    ColumnNotFoundError,
    TypeMismatchError,
)
from queries.services.types import RelationalSchema

from .conftest import assert_invalid, assert_valid


@pytest.mark.parametrize(
    'query',
    [
        'SELECT * FROM products WHERE product_id = 1',
        "SELECT * FROM products WHERE product_name = 'Test'",
        'SELECT * FROM products WHERE price > 10.5',
        'SELECT * FROM products WHERE in_stock = TRUE',
        'SELECT * FROM products WHERE product_id IN (1, 2, 3)',
        'SELECT * FROM products WHERE price > 10 AND in_stock = TRUE',
        "SELECT * FROM products WHERE price > 10 OR product_name = 'Test'",
        'SELECT * FROM products WHERE NOT in_stock',
        'SELECT * FROM products WHERE (price > 10 AND in_stock) OR product_id = 1',
    ],
)
def test_valid_where_conditions(query: str, schema: RelationalSchema) -> None:
    assert_valid(query, schema)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        ("SELECT * FROM products WHERE nonexistent_column = 'value'", ColumnNotFoundError),
        ('SELECT * FROM products WHERE product_name > 10', TypeMismatchError),
        ('SELECT * FROM products WHERE price = TRUE', TypeMismatchError),
        ('SELECT * FROM products WHERE 123', TypeMismatchError),  # Non-boolean expression
        (
            'SELECT * FROM products WHERE COUNT(*) > 5',
            AggregateInWhereError,
        ),  # Aggregate in WHERE
    ],
)
def test_invalid_where_conditions(
    query: str, expected_exception: type[Exception], schema: RelationalSchema
) -> None:
    assert_invalid(query, schema, expected_exception)
