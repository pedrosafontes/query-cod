import pytest
from queries.services.sql.semantics.errors import (
    ColumnNotFoundError,
    OrderByExpressionError,
)
from queries.services.types import RelationalSchema
from sqlglot.errors import OptimizeError

from .conftest import assert_invalid, assert_valid


@pytest.mark.parametrize(
    'query',
    [
        # Basic ORDER BY
        'SELECT * FROM products ORDER BY product_id',
        'SELECT * FROM products ORDER BY price DESC',
        # Multi-column ORDER BY
        'SELECT * FROM products ORDER BY category_id, price DESC',
        # ORDER BY position
        'SELECT product_id, product_name FROM products ORDER BY 1',
        'SELECT product_id, product_name FROM products ORDER BY 2 DESC',
        # ORDER BY expression
        'SELECT * FROM products ORDER BY price * 1.1',
        # ORDER BY alias
        'SELECT product_id AS id FROM products ORDER BY id',
        # ORDER BY with GROUP BY
        'SELECT category_id, COUNT(*) AS count FROM products GROUP BY category_id ORDER BY count',
        # ORDER BY with GROUP BY using aggregate function in ORDER BY but not in SELECT
        'SELECT category_id FROM products GROUP BY category_id ORDER BY COUNT(*) DESC',
    ],
)
def test_valid_order_by(query: str, schema: RelationalSchema) -> None:
    assert_valid(query, schema)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        # Non-existent column
        ('SELECT * FROM products ORDER BY nonexistent_column', ColumnNotFoundError),
        # Invalid ORDER BY position
        ('SELECT product_id FROM products ORDER BY 2', OptimizeError),
        # ORDER BY column not in SELECT with GROUP BY
        (
            'SELECT category_id, COUNT(*) FROM products GROUP BY category_id ORDER BY price',
            OrderByExpressionError,
        ),
    ],
)
def test_invalid_order_by(
    query: str, expected_exception: type[Exception], schema: RelationalSchema
) -> None:
    assert_invalid(query, schema, expected_exception)
