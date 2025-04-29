import pytest
from databases.types import Schema

from .conftest import assert_valid


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
def test_valid_complex_queries(query: str, schema: Schema) -> None:
    assert_valid(query, schema)
