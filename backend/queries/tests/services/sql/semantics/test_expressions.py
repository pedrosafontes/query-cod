import pytest
from queries.services.sql.semantics.errors import (
    ColumnCountMismatchError,
    ColumnNotFoundError,
    InvalidCastError,
    NonScalarExpressionError,
    TypeMismatchError,
)
from queries.services.types import RelationalSchema

from .conftest import assert_invalid, assert_valid


class TestQuantifiedSubqueries:
    @pytest.mark.parametrize(
        'query',
        [
            # ────── IN ──────
            # Valid IN with scalar subquery
            'SELECT * FROM products WHERE category_id NOT IN (SELECT category_id FROM categories)',
            # ────── ANY / SOME ──────
            # Valid comparison to scalar subquery result (same type)
            'SELECT * FROM products WHERE price > ANY (SELECT price FROM products)',
            # Valid integer comparison
            'SELECT * FROM products WHERE category_id = ANY (SELECT category_id FROM categories)',
            # Using SOME (synonym for ANY)
            'SELECT * FROM products WHERE price < SOME (SELECT price FROM products WHERE in_stock)',
            # Correlated ANY subquery
            'SELECT * FROM products p WHERE price < ANY (SELECT price FROM products WHERE category_id = p.category_id)',
            # ────── ALL ──────
            'SELECT * FROM products WHERE price <= ALL (SELECT price FROM products WHERE in_stock)',
            # ALL with subquery returning no rows should still be valid
            'SELECT * FROM products WHERE product_id > ALL (SELECT product_id FROM products WHERE 1 = 0)',
            # Correlated ALL subquery
            'SELECT * FROM customers c WHERE customer_id = ALL (SELECT customer_id FROM orders o WHERE quantity > 5 AND o.customer_id = c.customer_id)',
            # ────── EXISTS ──────
            # Basic EXISTS
            'SELECT * FROM products WHERE EXISTS (SELECT 1 FROM orders WHERE products.product_id = orders.product_id)',
            # EXISTS with constant expression
            'SELECT * FROM customers WHERE EXISTS (SELECT 1)',
            # EXISTS with non-correlated filter
            'SELECT * FROM categories WHERE EXISTS (SELECT * FROM products WHERE price > 100)',
            # Correlated EXISTS
            'SELECT * FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)',
            # EXISTS with scalar expression (allowed)
            'SELECT * FROM customers WHERE EXISTS (SELECT MAX(quantity) FROM orders)',
            # ────── Complex ──────
            # Nested
            """
            SELECT * FROM products
            WHERE EXISTS (
            SELECT 1 FROM orders
            WHERE orders.product_id = products.product_id
            AND quantity > ANY (
                SELECT quantity FROM orders WHERE customer_id = '123'
            )
            )
            """,
        ],
    )
    def test_valid_quantified_predicates(self, query: str, schema: RelationalSchema) -> None:
        assert_valid(query, schema)

    @pytest.mark.parametrize(
        'query, expected_exception',
        [
            # ────── IN ──────
            (
                'SELECT * FROM products WHERE category_id IN (SELECT category_id, category_name FROM categories)',
                ColumnCountMismatchError,
            ),
            # IN with incompatible types
            (
                'SELECT * FROM products WHERE category_id IN (SELECT category_name FROM categories)',
                TypeMismatchError,
            ),
            # ────── ANY / SOME ──────
            # ANY with non-comparable types
            (
                'SELECT * FROM products WHERE product_name = ANY (SELECT price FROM products)',
                TypeMismatchError,
            ),
            # ANY with multi-column subquery
            (
                'SELECT * FROM products WHERE product_id = ANY (SELECT product_id, price FROM products)',
                ColumnCountMismatchError,
            ),
            # ────── ALL ──────
            # ALL with incompatible types
            (
                'SELECT * FROM products WHERE price < ALL (SELECT product_name FROM products)',
                TypeMismatchError,
            ),
            # ALL with multi-column subquery
            (
                'SELECT * FROM products WHERE category_id = ALL (SELECT category_id, category_name FROM categories)',
                ColumnCountMismatchError,
            ),
        ],
    )
    def test_invalid_quantified_predicates(
        self, query: str, expected_exception: type[Exception], schema: RelationalSchema
    ) -> None:
        assert_invalid(query, schema, expected_exception)


class TestStringFunctions:
    @pytest.mark.parametrize(
        'query',
        [
            'SELECT CHAR_LENGTH(product_name) FROM products',
            'SELECT CHARACTER_LENGTH(product_name) FROM products',
            'SELECT LOWER(product_name) FROM products',
            'SELECT UPPER(product_name) FROM products',
            'SELECT TRIM(product_name) FROM products',
            'SELECT SUBSTRING(product_name FROM 1 FOR 3) FROM products',
            "SELECT POSITION('pro' IN product_name) FROM products",
            "SELECT product_name || ' (SALE)' FROM products",
        ],
    )
    def test_valid_string_functions(self, query: str, schema: RelationalSchema) -> None:
        assert_valid(query, schema)

    @pytest.mark.parametrize(
        'query, expected_exception',
        [
            ('SELECT CHAR_LENGTH(unknown_column) FROM products', ColumnNotFoundError),
            ("SELECT POSITION('x' IN 42) FROM products", TypeMismatchError),
            ('SELECT LOWER(*) FROM products', NonScalarExpressionError),
            ("SELECT SUBSTRING(product_name FROM 'x') FROM products", TypeMismatchError),
        ],
    )
    def test_invalid_string_functions(
        self, query: str, expected_exception: type[Exception], schema: RelationalSchema
    ) -> None:
        assert_invalid(query, schema, expected_exception)


class TestPredicateValidation:
    @pytest.mark.parametrize(
        'query',
        [
            'SELECT * FROM products WHERE price BETWEEN 10 AND 20',
            "SELECT * FROM products WHERE product_name LIKE 'A%'",
            'SELECT * FROM products WHERE category_id IS NULL',
            'SELECT * FROM products WHERE category_id IS NOT NULL',
        ],
    )
    def test_valid_predicates(self, query: str, schema: RelationalSchema) -> None:
        assert_valid(query, schema)

    @pytest.mark.parametrize(
        'query, expected_exception',
        [
            ("SELECT * FROM products WHERE price BETWEEN 'low' AND 'high'", TypeMismatchError),
            ('SELECT * FROM products WHERE product_name LIKE 123', TypeMismatchError),
        ],
    )
    def test_invalid_predicates(
        self, query: str, expected_exception: type[Exception], schema: RelationalSchema
    ) -> None:
        assert_invalid(query, schema, expected_exception)


class TestCastFunction:
    @pytest.mark.parametrize(
        'query',
        [
            'SELECT CAST(price AS INTEGER) FROM products',
            "SELECT CAST('2025-04-29' AS DATE)",
            'SELECT CAST(product_id AS VARCHAR) FROM products',
        ],
    )
    def test_valid_casts(self, query: str, schema: RelationalSchema) -> None:
        assert_valid(query, schema)

    @pytest.mark.parametrize(
        'query, expected_exception',
        [
            ('SELECT CAST(price AS DATE) FROM products', InvalidCastError),
        ],
    )
    def test_invalid_casts(
        self, query: str, expected_exception: type[Exception], schema: RelationalSchema
    ) -> None:
        assert_invalid(query, schema, expected_exception)
