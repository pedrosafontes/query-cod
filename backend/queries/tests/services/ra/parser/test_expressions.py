import pytest
from queries.services.ra.ast import (
    EQ,
    GT,
    GTE,
    LT,
    LTE,
    NEQ,
    Comparison,
    Relation,
    attribute,
)
from queries.services.ra.parser import parse_ra


@pytest.mark.parametrize(
    'op_str, expected_op',
    [
        ('=', EQ),
        ('\\neq', NEQ),
        ('<', LT),
        ('\\lt', LT),
        ('\\leq', LTE),
        ('>', GT),
        ('\\gt', GT),
        ('\\geq', GTE),
    ],
)
def test_comparison_operators(op_str: str, expected_op: type[Comparison]) -> None:
    # Use selection as a wrapper to test comparison expressions
    assert parse_ra(f'\\sigma_{{a {op_str} 5}} R') == Relation('R').select(
        expected_op(attribute('a'), 5)
    )
