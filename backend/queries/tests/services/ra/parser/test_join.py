import pytest
from queries.services.ra.ast import (
    EQ,
    GT,
    And,
    Join,
    JoinOperator,
    RAQuery,
    Relation,
    attribute,
)
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.errors import (
    InvalidThetaJoinConditionError,
    MissingOperandError,
    MissingThetaJoinConditionError,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        ('R \\Join S', Relation('R').natural_join('S')),
        ('R \\ltimes S', Relation('R').semi_join('S')),
        (
            'R \\overset{a = b}{\\bowtie} S',
            Relation('R').theta_join('S', EQ(attribute('a'), attribute('b'))),
        ),
        (
            'R \\overset{a > b \\land c = d}{\\bowtie} S',
            Relation('R').theta_join(
                'S',
                And(GT(attribute('a'), attribute('b')), EQ(attribute('c'), attribute('d'))),
            ),
        ),
        (
            'R \\Join (S \\Join T)',
            Relation('R').natural_join(Relation('S').natural_join('T')),
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
        (
            'R \\overline{\\Join} S',
            Relation('R').anti_join('S'),
        ),
    ],
)
def test_valid_join(query: str, expected: RAQuery) -> None:
    assert parse_ra(query) == expected


@pytest.mark.parametrize(
    'query, expected_error',
    [
        ('R \\overset{}{\\bowtie} S', MissingThetaJoinConditionError),
        ('R \\overset{a =}{\\bowtie} S', InvalidThetaJoinConditionError),
        ('R \\overset{= b}{\\bowtie} S', InvalidThetaJoinConditionError),
        ('\\Join S', MissingOperandError),
        ('R \\Join', MissingOperandError),
        ('R \\overline{\\Join}', MissingOperandError),
    ],
)
def test_invalid_join(query: str, expected_error: type) -> None:
    with pytest.raises(expected_error):
        parse_ra(query)
