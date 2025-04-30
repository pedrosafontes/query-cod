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
    RAExpression,
    Relation,
    ThetaJoin,
)
from queries.services.ra.parser.errors import (
    InvalidThetaJoinConditionError,
    MissingOperandError,
    MissingThetaJoinConditionError,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        ('R \\Join S', Join(JoinOperator.NATURAL, Relation('R'), Relation('S'))),
        ('R \\ltimes S', Join(JoinOperator.SEMI, Relation('R'), Relation('S'))),
        (
            'R \\overset{a = b}{\\bowtie} S',
            ThetaJoin(
                Relation('R'),
                Relation('S'),
                Comparison(ComparisonOperator.EQUAL, Attribute('a'), Attribute('b')),
            ),
        ),
        (
            'R \\overset{a > b \\land c = d}{\\bowtie} S',
            ThetaJoin(
                Relation('R'),
                Relation('S'),
                BinaryBooleanExpression(
                    BinaryBooleanOperator.AND,
                    Comparison(ComparisonOperator.GREATER_THAN, Attribute('a'), Attribute('b')),
                    Comparison(ComparisonOperator.EQUAL, Attribute('c'), Attribute('d')),
                ),
            ),
        ),
        (
            'R \\Join (S \\Join T)',
            Join(
                operator=JoinOperator.NATURAL,
                left=Relation('R'),
                right=Join(
                    operator=JoinOperator.NATURAL,
                    left=Relation('S'),
                    right=Relation('T'),
                ),
            ),
        ),
        (
            'R \\Join S \\Join T',
            Join(
                operator=JoinOperator.NATURAL,
                left=Join(
                    operator=JoinOperator.NATURAL,
                    left=Relation('R'),
                    right=Relation('S'),
                ),
                right=Relation('T'),
            ),  # assumes left-associative
        ),
    ],
)
def test_valid_join(query: str, expected: RAExpression) -> None:
    assert parse_ra(query) == expected


@pytest.mark.parametrize(
    'query, expected_error',
    [
        ('R \\overset{}{\\bowtie} S', MissingThetaJoinConditionError),
        ('R \\overset{a =}{\\bowtie} S', InvalidThetaJoinConditionError),
        ('R \\overset{= b}{\\bowtie} S', InvalidThetaJoinConditionError),
        ('\\Join S', MissingOperandError),
    ],
)
def test_invalid_join(query: str, expected_error: type) -> None:
    with pytest.raises(expected_error):
        parse_ra(query)
