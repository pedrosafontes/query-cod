import pytest
from databases.types import Schema
from queries.services.sql.semantics.errors import ColumnCountMismatchError, ColumnTypeMismatchError

from .conftest import assert_invalid, assert_valid


@pytest.mark.parametrize(
    'query',
    [
        # Valid UNIONs
        'SELECT product_id FROM products UNION SELECT product_id FROM orders',
        'SELECT customer_id FROM customers UNION SELECT customer_id FROM orders',
        # Valid INTERSECTs
        'SELECT product_id FROM products INTERSECT SELECT product_id FROM orders',
        'SELECT customer_id FROM customers INTERSECT SELECT customer_id FROM orders',
        # Valid EXCEPTs
        'SELECT product_id FROM products EXCEPT SELECT product_id FROM orders',
        'SELECT customer_id FROM customers EXCEPT SELECT customer_id FROM orders',
    ],
)
def test_valid_set_operations(query: str, schema: Schema) -> None:
    assert_valid(query, schema)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        # Mismatched number of columns
        (
            'SELECT product_id, price FROM products UNION SELECT product_id FROM orders',
            ColumnCountMismatchError,
        ),
        # Incompatible types in columns
        (
            'SELECT product_id FROM products UNION SELECT customer_id FROM customers',
            ColumnTypeMismatchError,
        ),
        (
            'SELECT product_name FROM products INTERSECT SELECT quantity FROM orders',
            ColumnTypeMismatchError,
        ),
        (
            'SELECT product_id FROM products EXCEPT SELECT name FROM customers',
            ColumnTypeMismatchError,
        ),
    ],
)
def test_invalid_set_operations(
    query: str, expected_exception: type[Exception], schema: Schema
) -> None:
    assert_invalid(query, schema, expected_exception)
