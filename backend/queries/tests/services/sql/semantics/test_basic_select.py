import pytest
from queries.services.sql.semantics.errors import (
    ColumnNotFoundError,
    DuplicateAliasError,
    NestedAggregateError,
    RelationNotFoundError,
)
from queries.services.types import RelationalSchema

from .conftest import assert_invalid, assert_valid


@pytest.mark.parametrize(
    'query',
    [
        'SELECT * FROM products',
        'SELECT product_id, product_name FROM products',
        'SELECT p.* FROM products p',
        'SELECT product_id AS id, product_name AS name FROM products',
        'SELECT product_id id, product_name name FROM products',  # Implicit alias
        'SELECT product_id, price * 1.1 AS increased_price FROM products',  # Expression
        'SELECT 1',  # Literal value without FROM
        "SELECT 1, 'hello' FROM products",  # Literal values
        "SELECT product_id, 'fixed label', price * 1.1 FROM products",  # Mixed
        'SELECT (price + 10) AS bumped_price FROM products',  # Expression
    ],
)
def test_valid_select_clauses(query: str, schema: RelationalSchema) -> None:
    assert_valid(query, schema)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        ('SELECT unknown_column FROM products', ColumnNotFoundError),
        ('SELECT * FROM nonexistent_table', RelationNotFoundError),
        ('SELECT product_id AS id, price AS id FROM products', DuplicateAliasError),
        ('SELECT COUNT(COUNT(*)) FROM products', NestedAggregateError),
    ],
)
def test_invalid_select_clauses(
    query: str, expected_exception: type[Exception], schema: RelationalSchema
) -> None:
    assert_invalid(query, schema, expected_exception)
