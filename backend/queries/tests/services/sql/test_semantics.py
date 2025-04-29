import pytest
from databases.types import Schema
from queries.services.sql.parser import parse_sql
from queries.services.sql.semantics import SQLSemanticAnalyzer
from queries.services.sql.semantics.errors import (
    AggregateInWhereError,
    AmbiguousColumnReferenceError,
    ColumnCountMismatchError,
    ColumnNotFoundError,
    ColumnTypeMismatchError,
    DuplicateAliasError,
    InvalidCastError,
    InvalidJoinConditionError,
    MissingDerivedColumnAliasError,
    MissingDerivedTableAliasError,
    MissingJoinConditionError,
    NestedAggregateError,
    NonScalarExpressionError,
    OrderByExpressionError,
    OrderByPositionError,
    RelationNotFoundError,
    TypeMismatchError,
    UngroupedColumnError,
)
from ra_sql_visualisation.types import DataType


@pytest.fixture
def schema() -> Schema:
    return {
        'products': {
            'product_id': DataType.INTEGER,
            'product_name': DataType.VARCHAR,
            'price': DataType.FLOAT,
            'category_id': DataType.INTEGER,
            'in_stock': DataType.BOOLEAN,
            'created_at': DataType.DATE,
            'binary_data': DataType.BIT_VARYING,
        },
        'categories': {
            'category_id': DataType.INTEGER,
            'category_name': DataType.VARCHAR,
        },
        'orders': {
            'order_id': DataType.INTEGER,
            'product_id': DataType.INTEGER,
            'customer_id': DataType.VARCHAR,
            'quantity': DataType.INTEGER,
            'order_date': DataType.DATE,
        },
        'customers': {
            'customer_id': DataType.VARCHAR,
            'name': DataType.VARCHAR,
            'country': DataType.VARCHAR,
        },
    }


def assert_valid(query: str, schema: Schema) -> None:
    select = parse_sql(query)
    print(select.to_s())
    SQLSemanticAnalyzer(schema).validate(select)


def assert_invalid(query: str, schema: Schema, exc: type[Exception]) -> None:
    select = parse_sql(query)
    print(select.to_s())
    with pytest.raises(exc):
        SQLSemanticAnalyzer(schema).validate(select)


class TestLiterals:
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
    def test_valid_literals(self, query: str, schema: Schema) -> None:
        assert_valid(query, schema)


class TestBasicSelects:
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
    def test_valid_select_clauses(self, query: str, schema: Schema) -> None:
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
        self, query: str, expected_exception: type[Exception], schema: Schema
    ) -> None:
        assert_invalid(query, schema, expected_exception)


class TestWhereConditions:
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
    def test_valid_where_conditions(self, query: str, schema: Schema) -> None:
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
        self, query: str, expected_exception: type[Exception], schema: Schema
    ) -> None:
        assert_invalid(query, schema, expected_exception)


class TestJoins:
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
    def test_valid_joins(self, query: str, schema: Schema) -> None:
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
        self, query: str, expected_exception: type[Exception], schema: Schema
    ) -> None:
        assert_invalid(query, schema, expected_exception)


class TestAggregatesAndGrouping:
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
    def test_valid_aggregates(self, query: str, schema: Schema) -> None:
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
        self, query: str, expected_exception: type[Exception], schema: Schema
    ) -> None:
        assert_invalid(query, schema, expected_exception)


class TestOrderBy:
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
    def test_valid_order_by(self, query: str, schema: Schema) -> None:
        assert_valid(query, schema)

    @pytest.mark.parametrize(
        'query, expected_exception',
        [
            # Non-existent column
            ('SELECT * FROM products ORDER BY nonexistent_column', ColumnNotFoundError),
            # Invalid ORDER BY position
            ('SELECT product_id FROM products ORDER BY 2', OrderByPositionError),
            # ORDER BY column not in SELECT with GROUP BY
            (
                'SELECT category_id, COUNT(*) FROM products GROUP BY category_id ORDER BY price',
                OrderByExpressionError,
            ),
        ],
    )
    def test_invalid_order_by(
        self, query: str, expected_exception: type[Exception], schema: Schema
    ) -> None:
        assert_invalid(query, schema, expected_exception)


class TestSubqueries:
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
    def test_valid_subqueries(self, query: str, schema: Schema) -> None:
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
        self, query: str, expected_exception: type[Exception], schema: Schema
    ) -> None:
        assert_invalid(query, schema, expected_exception)


# Comprehensive tests that combine multiple features
class TestComplexQueries:
    @pytest.mark.parametrize(
        'query',
        [
            # Complex query with JOIN, GROUP BY, and ORDER BY
            """
            SELECT c.category_name, COUNT(p.product_id) AS product_count, AVG(p.price) AS avg_price
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            WHERE p.price > 10
            GROUP BY c.category_name
            HAVING COUNT(p.product_id) > 2
            ORDER BY avg_price DESC
            """,
            # Multiple JOINs with subquery
            """
            SELECT p.product_name, c.category_name, o.order_date
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            JOIN orders o ON p.product_id = o.product_id
            WHERE p.price > (SELECT AVG(price) FROM products)
            ORDER BY o.order_date DESC
            """,
            # Subquery in FROM with JOIN
            """
            SELECT p.name, c.category_name
            FROM (SELECT product_id AS id, product_name AS name, category_id FROM products WHERE price > 100) AS p
            JOIN categories c ON p.category_id = c.category_id
            """,
            # Complex GROUP BY with multiple aggregate functions
            """
            SELECT c.category_name,
                   COUNT(p.product_id) AS count,
                   SUM(p.price) AS total_price,
                   AVG(p.price) AS avg_price,
                   MAX(p.price) AS max_price,
                   MIN(p.price) AS min_price
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            GROUP BY c.category_name
            ORDER BY count DESC, avg_price DESC
            """,
        ],
    )
    def test_valid_complex_queries(self, query: str, schema: Schema) -> None:
        assert_valid(query, schema)


class TestSetOperations:
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
    def test_valid_set_operations(self, query: str, schema: Schema) -> None:
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
        self, query: str, expected_exception: type[Exception], schema: Schema
    ) -> None:
        assert_invalid(query, schema, expected_exception)


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
    def test_valid_quantified_predicates(self, query: str, schema: Schema) -> None:
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
        self, query: str, expected_exception: type[Exception], schema: Schema
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
    def test_valid_string_functions(self, query: str, schema: Schema) -> None:
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
        self, query: str, expected_exception: type[Exception], schema: Schema
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
    def test_valid_predicates(self, query: str, schema: Schema) -> None:
        assert_valid(query, schema)

    @pytest.mark.parametrize(
        'query, expected_exception',
        [
            ("SELECT * FROM products WHERE price BETWEEN 'low' AND 'high'", TypeMismatchError),
            ('SELECT * FROM products WHERE product_name LIKE 123', TypeMismatchError),
        ],
    )
    def test_invalid_predicates(
        self, query: str, expected_exception: type[Exception], schema: Schema
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
    def test_valid_casts(self, query: str, schema: Schema) -> None:
        assert_valid(query, schema)

    @pytest.mark.parametrize(
        'query, expected_exception',
        [
            ('SELECT CAST(price AS DATE) FROM products', InvalidCastError),
        ],
    )
    def test_invalid_casts(
        self, query: str, expected_exception: type[Exception], schema: Schema
    ) -> None:
        assert_invalid(query, schema, expected_exception)
