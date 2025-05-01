import pytest
from queries.services.sql.semantics.errors import (
    ColumnNotFoundError,
    MissingDerivedColumnAliasError,
    MissingDerivedTableAliasError,
    NonScalarExpressionError,
    TypeMismatchError,
)
from queries.services.types import RelationalSchema

from .conftest import assert_invalid, assert_valid


@pytest.mark.parametrize(
    'query',
    [
        # Scalar subquery in WHERE
        'SELECT * FROM products WHERE price > (SELECT AVG(price) FROM products)',
        # Subquery in FROM
        'SELECT * FROM (SELECT product_id, price FROM products) AS p',
        # Correlated subquery
        'SELECT * FROM products p WHERE price > (SELECT AVG(price) FROM products WHERE category_id = p.category_id)',
        # Subquery with alias in FROM
        'SELECT p.id, p.name FROM (SELECT product_id AS id, product_name AS name FROM products) AS p',
        # Multiple subqueries
        'SELECT * FROM products WHERE category_id IN (SELECT category_id FROM categories) AND price > (SELECT AVG(price) FROM products)',
        # Nested subqueries
        'SELECT * FROM products WHERE category_id IN (SELECT category_id FROM categories WHERE category_id IN (SELECT category_id FROM products GROUP BY category_id HAVING COUNT(*) > 5))',
    ],
)
def test_valid_subqueries(query: str, schema: RelationalSchema) -> None:
    assert_valid(query, schema)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        # Missing alias for derived table
        ('SELECT * FROM (SELECT * FROM products)', MissingDerivedTableAliasError),
        # Non-scalar subquery in comparison
        (
            'SELECT * FROM products WHERE price = (SELECT price FROM products)',
            NonScalarExpressionError,
        ),
        # Missing alias for derived column
        (
            'SELECT * FROM (SELECT product_id, price * 1.1 FROM products) AS p',
            MissingDerivedColumnAliasError,
        ),
        # Undefined column in subquery
        (
            'SELECT * FROM products WHERE price > (SELECT AVG(unknown_column) FROM products)',
            ColumnNotFoundError,
        ),
        # Subquery type mismatch
        (
            'SELECT * FROM products WHERE product_name = (SELECT COUNT(*) FROM orders)',
            TypeMismatchError,
        ),
    ],
)
def test_invalid_subqueries(
    query: str, expected_exception: type[Exception], schema: RelationalSchema
) -> None:
    assert_invalid(query, schema, expected_exception)
