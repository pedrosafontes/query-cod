import pytest
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.ast import (
    Attribute,
    BinaryBooleanExpression,
    BinaryBooleanOperator,
    Comparison,
    ComparisonOperator,
    Join,
    JoinOperator,
    NotExpression,
    RAQuery,
    Relation,
    Selection,
)
from queries.services.ra.parser.errors import (
    InvalidSelectionConditionError,
    MissingSelectionConditionError,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        (
            '\\sigma_{a = 5} R',
            Selection(Comparison(ComparisonOperator.EQUAL, Attribute('a'), 5), Relation('R')),
        ),
        (
            '\\sigma_{salary > 50000} Employee',
            Selection(
                Comparison(ComparisonOperator.GREATER_THAN, Attribute('salary'), 50000),
                Relation('Employee'),
            ),
        ),
        (
            "\\sigma_{name = \\text{'John'}} Employee",
            Selection(
                Comparison(ComparisonOperator.EQUAL, Attribute('name'), 'John'),
                Relation('Employee'),
            ),
        ),
        (
            '\\sigma_{Employee.salary > Department.budget} (Employee \\Join Department)',
            Selection(
                Comparison(
                    ComparisonOperator.GREATER_THAN,
                    Attribute('salary', relation='Employee'),
                    Attribute('budget', relation='Department'),
                ),
                Join(JoinOperator.NATURAL, Relation('Employee'), Relation('Department')),
            ),
        ),
        (
            '\\sigma_{a = 5 \\land b = 10} R',
            Selection(
                BinaryBooleanExpression(
                    BinaryBooleanOperator.AND,
                    Comparison(ComparisonOperator.EQUAL, Attribute('a'), 5),
                    Comparison(ComparisonOperator.EQUAL, Attribute('b'), 10),
                ),
                Relation('R'),
            ),
        ),
        (
            '\\sigma_{a = 5 \\lor b = 10} R',
            Selection(
                BinaryBooleanExpression(
                    BinaryBooleanOperator.OR,
                    Comparison(ComparisonOperator.EQUAL, Attribute('a'), 5),
                    Comparison(ComparisonOperator.EQUAL, Attribute('b'), 10),
                ),
                Relation('R'),
            ),
        ),
        (
            '\\sigma_{\\lnot (a = 5)} R',
            Selection(
                NotExpression(Comparison(ComparisonOperator.EQUAL, Attribute('a'), 5)),
                Relation('R'),
            ),
        ),
        (
            "\\sigma_{(a = 5 \\land b > 10) \\lor c = \\text{'test'}} R",
            Selection(
                BinaryBooleanExpression(
                    BinaryBooleanOperator.OR,
                    BinaryBooleanExpression(
                        BinaryBooleanOperator.AND,
                        Comparison(ComparisonOperator.EQUAL, Attribute('a'), 5),
                        Comparison(ComparisonOperator.GREATER_THAN, Attribute('b'), 10),
                    ),
                    Comparison(ComparisonOperator.EQUAL, Attribute('c'), 'test'),
                ),
                Relation('R'),
            ),
        ),
        (
            '\\sigma_{\\lnot (a = 5 \\lor b = 10) \\land c > 20} R',
            Selection(
                BinaryBooleanExpression(
                    BinaryBooleanOperator.AND,
                    NotExpression(
                        BinaryBooleanExpression(
                            BinaryBooleanOperator.OR,
                            Comparison(ComparisonOperator.EQUAL, Attribute('a'), 5),
                            Comparison(ComparisonOperator.EQUAL, Attribute('b'), 10),
                        )
                    ),
                    Comparison(ComparisonOperator.GREATER_THAN, Attribute('c'), 20),
                ),
                Relation('R'),
            ),
        ),
        (
            '\\sigma_{a = 1 \\lor b = 2 \\land c = 3} R',
            Selection(
                BinaryBooleanExpression(
                    BinaryBooleanOperator.OR,
                    Comparison(ComparisonOperator.EQUAL, Attribute('a'), 1),
                    BinaryBooleanExpression(
                        BinaryBooleanOperator.AND,
                        Comparison(ComparisonOperator.EQUAL, Attribute('b'), 2),
                        Comparison(ComparisonOperator.EQUAL, Attribute('c'), 3),
                    ),
                ),
                Relation('R'),
            ),
        ),
        (
            '\\sigma_{Sailor.rating > 7} (Sailor \\Join Boat)',
            Selection(
                condition=Comparison(
                    operator=ComparisonOperator.GREATER_THAN,
                    left=Attribute('rating', relation='Sailor'),
                    right=7,
                ),
                sub_query=Join(
                    operator=JoinOperator.NATURAL,
                    left=Relation('Sailor'),
                    right=Relation('Boat'),
                ),
            ),
        ),
        ('\\sigma_{a} R', Selection(Attribute('a'), Relation('R'))),
    ],
)
def test_valid_selection(query: str, expected: RAQuery) -> None:
    assert parse_ra(query) == expected


@pytest.mark.parametrize(
    'query, expected_error',
    [
        ('\\sigma_{} R', MissingSelectionConditionError),
        ('\\sigma R', MissingSelectionConditionError),
        ('\\sigma_{a >} R', InvalidSelectionConditionError),
        ('\\sigma_{=} R', InvalidSelectionConditionError),
        ('\\sigma_{a == b} R', InvalidSelectionConditionError),
    ],
)
def test_invalid_selection(query: str, expected_error: type) -> None:
    with pytest.raises(expected_error):
        parse_ra(query)
