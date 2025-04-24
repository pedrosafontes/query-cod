import pytest
from databases.types import DataType, Schema
from queries.services.sql.parser import parse_sql
from queries.services.sql.validation.errors import (
    AmbiguousColumnError,
    CrossJoinConditionError,
    DerivedColumnAliasRequiredError,
    DuplicateAliasError,
    GroupByClauseRequiredError,
    MissingDerivedTableAliasError,
    MissingJoinConditionError,
    NoCommonColumnsError,
    NonGroupedColumnError,
    OrderByExpressionError,
    OrderByPositionError,
    ScalarSubqueryError,
    TypeMismatchError,
    UndefinedColumnError,
    UndefinedTableError,
    UnorderableTypeError,
)
from queries.services.sql.validation.semantics import SQLSemanticAnalyzer


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
    SQLSemanticAnalyzer(schema).validate(select)


def assert_invalid(query: str, schema: Schema, exc: type[Exception]) -> None:
    select = parse_sql(query)
    with pytest.raises(exc):
        SQLSemanticAnalyzer(schema).validate(select)


class TestBasicSelects:
    @pytest.mark.parametrize(
        'query',
        [
            'SELECT * FROM products',
            'SELECT product_id, product_name FROM products',
            'SELECT product_id AS id, product_name AS name FROM products',
            'SELECT product_id id, product_name name FROM products',  # Implicit alias
            'SELECT product_id, price * 1.1 AS increased_price FROM products',  # Expression
        ],
    )
    def test_valid_select_clauses(self, query: str, schema: Schema) -> None:
        assert_valid(query, schema)

    @pytest.mark.parametrize(
        'query, expected_exception',
        [
            ('SELECT unknown_column FROM products', UndefinedColumnError),
            ('SELECT * FROM nonexistent_table', UndefinedTableError),
            ('SELECT product_id AS id, price AS id FROM products', DuplicateAliasError),
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
            "SELECT * FROM products WHERE price > 10 OR product_name = 'Test'",
            'SELECT * FROM products WHERE NOT in_stock',
        ],
    )
    def test_valid_where_conditions(self, query: str, schema: Schema) -> None:
        assert_valid(query, schema)

    @pytest.mark.parametrize(
        'query, expected_exception',
        [
            ("SELECT * FROM products WHERE nonexistent_column = 'value'", UndefinedColumnError),
            ('SELECT * FROM products WHERE product_name > 10', TypeMismatchError),
            ('SELECT * FROM products WHERE 123', TypeMismatchError),  # Non-boolean expression
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
            # Multiple JOINs
            'SELECT * FROM products p JOIN orders o ON p.product_id = o.product_id JOIN customers c ON o.customer_id = c.customer_id',
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
                CrossJoinConditionError,
            ),
            # Ambiguous columns
            (
                'SELECT category_id FROM products JOIN categories ON products.category_id = categories.category_id',
                AmbiguousColumnError,
            ),
            # No common columns for NATURAL JOIN
            ('SELECT * FROM products NATURAL JOIN customers', NoCommonColumnsError),
            # Non-boolean JOIN condition
            ('SELECT * FROM products p JOIN categories c ON p.product_id', TypeMismatchError),
            # USING on non-existent column
            (
                'SELECT * FROM products JOIN categories USING (nonexistent_column)',
                UndefinedColumnError,
            ),
            # Ambiguous columns in SELECT with JOIN
            (
                'SELECT customer_id FROM customers c JOIN orders o ON c.customer_id = o.customer_id',
                AmbiguousColumnError,
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
            # 'SELECT MIN(price), MAX(price) FROM products',
            # Group BY
            'SELECT category_id, COUNT(*) FROM products GROUP BY category_id',
            'SELECT category_id, AVG(price) FROM products GROUP BY category_id',
            'SELECT category_id, product_name, COUNT(*) FROM products GROUP BY category_id, product_name',
            # HAVING
            'SELECT category_id, COUNT(*) FROM products GROUP BY category_id HAVING COUNT(*) > 5',
            'SELECT category_id, AVG(price) FROM products GROUP BY category_id HAVING AVG(price) > 100',
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
                NonGroupedColumnError,
            ),
            # Non-existent column in GROUP BY
            ('SELECT COUNT(*) FROM products GROUP BY nonexistent_column', UndefinedColumnError),
            # Invalid aggregate argument
            ('SELECT SUM(product_name) FROM products', TypeMismatchError),
            # HAVING without GROUP BY
            ('SELECT COUNT(*) FROM products HAVING COUNT(*) > 5', GroupByClauseRequiredError),
            # Non-grouped column in HAVING
            (
                "SELECT category_id FROM products GROUP BY category_id HAVING product_name = 'test'",
                NonGroupedColumnError,
            ),
            # Invalid HAVING condition type
            (
                "SELECT category_id FROM products GROUP BY category_id HAVING COUNT(*) = 'test'",
                TypeMismatchError,
            ),
            (
                'SELECT * FROM categories GROUP BY category_id',
                NonGroupedColumnError,
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
            # ORDER BY with GROUP BY
            'SELECT category_id, COUNT(*) AS count FROM products GROUP BY category_id ORDER BY count',
        ],
    )
    def test_valid_order_by(self, query: str, schema: Schema) -> None:
        assert_valid(query, schema)

    @pytest.mark.parametrize(
        'query, expected_exception',
        [
            # Non-existent column
            ('SELECT * FROM products ORDER BY nonexistent_column', UndefinedColumnError),
            # Invalid ORDER BY position
            ('SELECT product_id FROM products ORDER BY 2', OrderByPositionError),
            # Unorderable data type
            ('SELECT * FROM products ORDER BY binary_data', UnorderableTypeError),
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
                ScalarSubqueryError,
            ),
            # Missing alias for derived column
            (
                'SELECT * FROM (SELECT product_id, price * 1.1 FROM products) AS p',
                DerivedColumnAliasRequiredError,
            ),
            # Undefined column in subquery
            (
                'SELECT * FROM products WHERE price > (SELECT AVG(unknown_column) FROM products)',
                UndefinedColumnError,
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
        select = parse_sql(query)
        SQLSemanticAnalyzer(schema).validate(select)
