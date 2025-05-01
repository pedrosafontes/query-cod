import pytest
from queries.services.sql.semantics.errors import (
    ColumnNotFoundError,
    TypeMismatchError,
    UngroupedColumnError,
)
from queries.services.types import RelationalSchema

from .conftest import assert_invalid, assert_valid


@pytest.mark.parametrize(
    'query',
    [
        # Basic aggregates
        'SELECT COUNT(*) FROM products',
        'SELECT SUM(price) FROM products',
        'SELECT AVG(price) FROM products',
        'SELECT MIN(price), MAX(price) FROM products',
        # Group BY
        'SELECT category_id, COUNT(*) FROM products GROUP BY category_id',
        'SELECT category_id, AVG(price) FROM products GROUP BY category_id',
        'SELECT category_id, product_name, COUNT(*) FROM products GROUP BY category_id, product_name',
        # HAVING
        'SELECT category_id, COUNT(*) FROM products GROUP BY category_id HAVING COUNT(*) > 5',
        'SELECT category_id, AVG(price) FROM products GROUP BY category_id HAVING AVG(price) > 100',
        # Multiple aggregate functions
        'SELECT category_id, COUNT(*), SUM(price), AVG(price) FROM products GROUP BY category_id',
        # Expressions in GROUP BY and HAVING
        'SELECT category_id, price / 2 AS half_price FROM products GROUP BY category_id, price / 2',
        'SELECT category_id, COUNT(*) FROM products GROUP BY category_id HAVING SUM(price) / COUNT(*) > 50',
    ],
)
def test_valid_aggregates(query: str, schema: RelationalSchema) -> None:
    assert_valid(query, schema)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        # Non-grouped column in SELECT
        (
            'SELECT product_id, category_id, COUNT(*) FROM products GROUP BY category_id',
            UngroupedColumnError,
        ),
        # Non-existent column in GROUP BY
        ('SELECT COUNT(*) FROM products GROUP BY nonexistent_column', ColumnNotFoundError),
        # Invalid aggregate argument
        ('SELECT SUM(product_name) FROM products', TypeMismatchError),
        # Non-grouped column in HAVING
        (
            "SELECT category_id FROM products GROUP BY category_id HAVING product_name = 'test'",
            UngroupedColumnError,
        ),
        # Invalid HAVING condition type
        (
            "SELECT category_id FROM products GROUP BY category_id HAVING COUNT(*) = 'test'",
            TypeMismatchError,
        ),
        (
            'SELECT * FROM categories GROUP BY category_id',
            UngroupedColumnError,
        ),
    ],
)
def test_invalid_aggregates(
    query: str, expected_exception: type[Exception], schema: RelationalSchema
) -> None:
    assert_invalid(query, schema, expected_exception)
