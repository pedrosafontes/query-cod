import pytest
from databases.types import DataType, Schema
from queries.services.sql.parser import parse_sql
from queries.services.sql.validation.errors import (
    AmbiguousColumnError,
    GroupByError,
    OrderByPositionError,
    SQLSemanticError,
    TypeMismatchError,
    UndefinedColumnError,
    UndefinedTableError,
)
from queries.services.sql.validation.semantics import SQLSemanticAnalyzer


@pytest.fixture
def schema() -> Schema:
    return {
        'categories': {
            'category_id': DataType.INTEGER,
            'category_name': DataType.VARCHAR,
            'description': DataType.VARCHAR,
            'picture': DataType.BIT_VARYING,
        },
        'customers': {
            'customer_id': DataType.VARCHAR,
            'company_name': DataType.VARCHAR,
            'contact_name': DataType.VARCHAR,
            'contact_title': DataType.VARCHAR,
            'address': DataType.VARCHAR,
            'city': DataType.VARCHAR,
            'region': DataType.VARCHAR,
            'postal_code': DataType.VARCHAR,
            'country': DataType.VARCHAR,
            'phone': DataType.VARCHAR,
            'fax': DataType.VARCHAR,
        },
        'employees': {
            'employee_id': DataType.INTEGER,
            'last_name': DataType.VARCHAR,
            'first_name': DataType.VARCHAR,
            'title': DataType.VARCHAR,
            'title_of_courtesy': DataType.VARCHAR,
            'birth_date': DataType.DATE,
            'hire_date': DataType.DATE,
            'address': DataType.VARCHAR,
            'city': DataType.VARCHAR,
            'region': DataType.VARCHAR,
            'postal_code': DataType.VARCHAR,
            'country': DataType.VARCHAR,
            'home_phone': DataType.VARCHAR,
            'extension': DataType.VARCHAR,
            'photo': DataType.BIT_VARYING,
            'notes': DataType.VARCHAR,
            'reports_to': DataType.INTEGER,
        },
        'suppliers': {
            'supplier_id': DataType.INTEGER,
            'company_name': DataType.VARCHAR,
            'contact_name': DataType.VARCHAR,
            'contact_title': DataType.VARCHAR,
            'address': DataType.VARCHAR,
            'city': DataType.VARCHAR,
            'region': DataType.VARCHAR,
            'postal_code': DataType.VARCHAR,
            'country': DataType.VARCHAR,
            'phone': DataType.VARCHAR,
            'fax': DataType.VARCHAR,
            'homepage': DataType.VARCHAR,
        },
        'products': {
            'product_id': DataType.INTEGER,
            'product_name': DataType.VARCHAR,
            'supplier_id': DataType.INTEGER,
            'category_id': DataType.INTEGER,
            'quantity_per_unit': DataType.VARCHAR,
            'unit_price': DataType.FLOAT,
            'units_in_stock': DataType.INTEGER,
            'units_on_order': DataType.INTEGER,
            'reorder_level': DataType.INTEGER,
            'discontinued': DataType.INTEGER,
        },
        'orders': {
            'order_id': DataType.INTEGER,
            'customer_id': DataType.VARCHAR,
            'employee_id': DataType.INTEGER,
            'order_date': DataType.DATE,
            'required_date': DataType.DATE,
            'shipped_date': DataType.DATE,
            'ship_via': DataType.INTEGER,
            'freight': DataType.FLOAT,
            'ship_name': DataType.VARCHAR,
            'ship_address': DataType.VARCHAR,
            'ship_city': DataType.VARCHAR,
            'ship_region': DataType.VARCHAR,
            'ship_postal_code': DataType.VARCHAR,
            'ship_country': DataType.VARCHAR,
        },
        'order_details': {
            'order_id': DataType.INTEGER,
            'product_id': DataType.INTEGER,
            'unit_price': DataType.FLOAT,
            'quantity': DataType.INTEGER,
            'discount': DataType.FLOAT,
        },
    }


@pytest.mark.parametrize(
    'query',
    [
        'SELECT * FROM customers',
        'SELECT customer_id, company_name FROM customers',
        "SELECT * FROM customers WHERE customer_id = '123abc'",
        "SELECT * FROM customers WHERE company_name = 'ABC Corp'",
        'SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id',
        'SELECT c.customer_id, o.order_id FROM customers c JOIN orders o ON c.customer_id = o.customer_id',
        'SELECT COUNT(*) FROM customers',
        'SELECT customer_id FROM customers ORDER BY company_name',
    ],
)
def test_valid_queries(query: str, schema: Schema) -> None:
    select = parse_sql(query)
    print(select.to_s())
    # Should not raise any exception
    SQLSemanticAnalyzer(schema).validate(select)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        ('SELECT * FROM nonexistent_table', UndefinedTableError),
        ('SELECT unknown_column FROM customers', UndefinedColumnError),
        ("SELECT * FROM customers WHERE nonexistent_column = 'value'", UndefinedColumnError),
        ('SELECT * FROM customers WHERE company_name > 10', TypeMismatchError),
        ('SELECT * FROM customers WHERE employee_id = 1', UndefinedColumnError),
        (
            'SELECT * FROM customers c JOIN orders o ON c.nonexistent_column = o.order_id',
            UndefinedColumnError,
        ),
        (
            'SELECT * FROM customers c JOIN orders o ON c.company_name = o.order_id',
            TypeMismatchError,
        ),
        (
            'SELECT * FROM customers c JOIN nonexistent_table n ON c.customer_id = n.id',
            UndefinedTableError,
        ),
        (
            'SELECT customer_id FROM customers JOIN orders ON customer_id = customer_id',
            AmbiguousColumnError,
        ),
        (
            'SELECT customer_id, company_name, COUNT(*) FROM customers GROUP BY customer_id',
            GroupByError,
        ),
        ('SELECT COUNT(*) FROM customers GROUP BY nonexistent_column', UndefinedColumnError),
        (
            'SELECT customer_id FROM customers GROUP BY customer_id HAVING nonexistent_column > 10',
            UndefinedColumnError,
        ),
        (
            'SELECT customer_id, COUNT(*) FROM customers GROUP BY customer_id HAVING SUM(company_name) > 10',
            TypeMismatchError,
        ),
        (
            "SELECT customer_id FROM customers GROUP BY customer_id HAVING COUNT(*) > 'text'",
            TypeMismatchError,
        ),
        (
            "SELECT customer_id FROM customers GROUP BY customer_id HAVING MAX(order_date) > '2020-01-01'",
            UndefinedColumnError,
        ),
        ('SELECT customer_id FROM customers HAVING COUNT(*) > 5', SQLSemanticError),
        # (
        #     'SELECT COUNT(COUNT(*)) FROM customers',
        #     SQLSemanticError
        # ),
        (
            'SELECT * FROM customers ORDER BY nonexistent_column',
            UndefinedColumnError,
        ),
        ('SELECT customer_id FROM customers ORDER BY order_id', UndefinedColumnError),
        (
            'SELECT customer_id, company_name FROM customers ORDER BY 3',
            OrderByPositionError,
        ),
    ],
)
def test_semantic_errors(query: str, expected_exception: type[Exception], schema: Schema) -> None:
    select = parse_sql(query)
    print(select.to_s())
    with pytest.raises(expected_exception):
        SQLSemanticAnalyzer(schema).validate(select)
