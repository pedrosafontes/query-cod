import pytest
from queries.services.ra.ast import (
    EQ,
    GT,
    And,
    Not,
    Or,
    RAQuery,
    Relation,
    attribute,
)
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.errors import (
    InvalidSelectionConditionError,
    MissingSelectionConditionError,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        (
            '\\sigma_{a = 5} R',
            Relation('R').select(EQ(attribute('a'), 5)),
        ),
        (
            '\\sigma_{salary > 50000} Employee',
            Relation('Employee').select(GT(attribute('salary'), 50000)),
        ),
        (
            "\\sigma_{name = \\text{'John'}} Employee",
            Relation('Employee').select(EQ(attribute('name'), 'John')),
        ),
        (
            '\\sigma_{Employee.salary > Department.budget} (Employee \\Join Department)',
            Relation('Employee')
            .natural_join('Department')
            .select(
                GT(
                    attribute('Employee.salary'),
                    attribute('Department.budget'),
                )
            ),
        ),
        (
            '\\sigma_{a = 5 \\land b = 10} R',
            Relation('R').select(
                And(
                    EQ(attribute('a'), 5),
                    EQ(attribute('b'), 10),
                )
            ),
        ),
        (
            '\\sigma_{a = 5 \\lor b = 10} R',
            Relation('R').select(
                Or(
                    EQ(attribute('a'), 5),
                    EQ(attribute('b'), 10),
                )
            ),
        ),
        (
            '\\sigma_{\\lnot (a = 5)} R',
            Relation('R').select(Not(EQ(attribute('a'), 5))),
        ),
        (
            "\\sigma_{(a = 5 \\land b > 10) \\lor c = \\text{'test'}} R",
            Relation('R').select(
                Or(
                    And(
                        EQ(attribute('a'), 5),
                        GT(attribute('b'), 10),
                    ),
                    EQ(attribute('c'), 'test'),
                )
            ),
        ),
        (
            '\\sigma_{\\lnot (a = 5 \\lor b = 10) \\land c > 20} R',
            Relation('R').select(
                And(
                    Not(
                        Or(
                            EQ(attribute('a'), 5),
                            EQ(attribute('b'), 10),
                        )
                    ),
                    GT(attribute('c'), 20),
                )
            ),
        ),
        (
            '\\sigma_{a = 1 \\lor b = 2 \\land c = 3} R',
            Relation('R').select(
                Or(
                    EQ(attribute('a'), 1),
                    And(
                        EQ(attribute('b'), 2),
                        EQ(attribute('c'), 3),
                    ),
                )
            ),
        ),
        (
            '\\sigma_{Sailor.rating > 7} (Sailor \\Join Boat)',
            Relation('Sailor').natural_join('Boat').select(GT(attribute('Sailor.rating'), 7)),
        ),
        ('\\sigma_{a} R', Relation('R').select(attribute('a'))),
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
