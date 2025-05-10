import pytest
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.ast import (
    Attribute,
    Comparison,
    ComparisonOperator,
    Relation,
    Selection,
)


@pytest.mark.parametrize(
    'op_str, expected_op',
    [
        ('=', ComparisonOperator.EQUAL),
        ('\\neq', ComparisonOperator.NOT_EQUAL),
        ('<', ComparisonOperator.LESS_THAN),
        ('\\lt', ComparisonOperator.LESS_THAN),
        ('\\leq', ComparisonOperator.LESS_THAN_EQUAL),
        ('>', ComparisonOperator.GREATER_THAN),
        ('\\gt', ComparisonOperator.GREATER_THAN),
        ('\\geq', ComparisonOperator.GREATER_THAN_EQUAL),
    ],
)
def test_comparison_operators(op_str: str, expected_op: ComparisonOperator) -> None:
    # Use selection as a wrapper to test comparison expressions
    assert parse_ra(f'\\sigma_{{a {op_str} 5}} R') == Selection(
        condition=Comparison(expected_op, Attribute('a'), 5),
        sub_query=Relation('R'),
    )
