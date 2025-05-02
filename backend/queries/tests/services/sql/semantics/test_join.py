import pytest
from queries.services.sql.semantics.errors import (
    AmbiguousColumnReferenceError,
    ColumnNotFoundError,
    InvalidJoinConditionError,
    MissingJoinConditionError,
    TypeMismatchError,
)
from queries.services.types import RelationalSchema

from .conftest import assert_invalid, assert_valid


@pytest.mark.parametrize(
    'query',
    [
        # Basic JOIN variants
        'SELECT * FROM products p JOIN categories c ON p.category_id = c.category_id',
        'SELECT * FROM products p LEFT JOIN categories c ON p.category_id = c.category_id',
        'SELECT * FROM products p RIGHT JOIN categories c ON p.category_id = c.category_id',
        'SELECT * FROM products p FULL JOIN categories c ON p.category_id = c.category_id',
        'SELECT * FROM products p CROSS JOIN categories c',
        # USING clause and NATURAL JOINs
        'SELECT * FROM products JOIN orders USING (product_id)',
        'SELECT * FROM products NATURAL JOIN orders',
        'SELECT product_id FROM products JOIN orders USING (product_id)',
        'SELECT product_id FROM products NATURAL JOIN orders',
        # Multiple JOINs
        'SELECT * FROM products p JOIN orders o ON p.product_id = o.product_id JOIN customers c ON o.customer_id = c.customer_id',
        # Self JOIN
        'SELECT p1.product_name, p2.product_name FROM products p1 JOIN products p2 ON p1.category_id = p2.category_id AND p1.product_id <> p2.product_id',
    ],
)
def test_valid_joins(query: str, schema: RelationalSchema) -> None:
    assert_valid(query, schema)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        # Missing JOIN condition
        ('SELECT * FROM products p JOIN categories c', MissingJoinConditionError),
        # Invalid JOIN condition
        (
            'SELECT * FROM products p JOIN categories c ON p.product_name = c.category_id',
            TypeMismatchError,
        ),
        # CROSS JOIN with condition
        (
            'SELECT * FROM products CROSS JOIN categories ON products.category_id = categories.category_id',
            InvalidJoinConditionError,
        ),
        # Ambiguous columns
        (
            'SELECT category_id FROM products JOIN categories ON products.category_id = categories.category_id',
            AmbiguousColumnReferenceError,
        ),
        # Non-boolean JOIN condition
        ('SELECT * FROM products p JOIN categories c ON p.product_id', TypeMismatchError),
        # USING on non-existent column
        (
            'SELECT * FROM products JOIN categories USING (nonexistent_column)',
            ColumnNotFoundError,
        ),
        # Ambiguous columns in SELECT with JOIN
        (
            'SELECT customer_id FROM customers c JOIN orders o ON c.customer_id = o.customer_id',
            AmbiguousColumnReferenceError,
        ),
    ],
)
def test_invalid_joins(
    query: str, expected_exception: type[Exception], schema: RelationalSchema
) -> None:
    assert_invalid(query, schema, expected_exception)
