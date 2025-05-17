import pytest
from queries.services.sql.parser import parse_sql
from queries.services.sql.semantics import QueryValidator
from queries.services.types import RelationalSchema
from ra_sql_visualisation.types import DataType


@pytest.fixture
def schema() -> RelationalSchema:
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


def assert_valid(query: str, schema: RelationalSchema) -> None:
    select = parse_sql(query)
    print(select.to_s())
    QueryValidator(schema).validate(select)


def assert_invalid(query: str, schema: RelationalSchema, exc: type[Exception]) -> None:
    select = parse_sql(query)
    print(select.to_s())
    with pytest.raises(exc):
        QueryValidator(schema).validate(select)
