import pytest
from queries.services.ra.ast import (
    EQ,
    Join,
    JoinOperator,
    RAQuery,
    Relation,
    SetOperation,
    SetOperator,
    attribute,
)
from queries.services.ra.parser import parse_ra


@pytest.mark.parametrize(
    'query, expected',
    [
        # Test basic projection precedence
        (
            '\\pi_{A} R - \\pi_{A} S',
            Relation('R').project('A').difference(Relation('S').project('A')),
        ),
        # Test parenthesized expressions
        (
            '\\pi_{A} (R - S)',
            Relation('R').difference(Relation('S')).project('A'),
        ),
        # Test operator associativity (left-to-right)
        (
            'R \\cup S - T',
            Relation('R').union('S').difference('T'),
        ),
        # Test join precedence with set operations
        (
            'R \\Join S - T \\Join U',
            SetOperation(
                operator=SetOperator.DIFFERENCE,
                left=Relation('R').natural_join('S'),
                right=Relation('T').natural_join('U'),
            ),
        ),
        # Test operator precedence mix
        (
            'R \\cap S \\cup T',
            Relation('R').intersect('S').union('T'),
        ),
        # Test projection vs set operation precedence
        (
            '\\pi_{A,B} R \\cup \\pi_{C,D} S',
            SetOperation(
                operator=SetOperator.UNION,
                left=Relation('R').project(['A', 'B']),
                right=Relation('S').project(['C', 'D']),
            ),
        ),
        # Test division with other operators
        (
            'R \\div S \\times T',
            SetOperation(
                operator=SetOperator.CARTESIAN,
                left=Relation('R').divide('S'),
                right=Relation('T'),
            ),
        ),
        # Test semi-join with projection
        (
            '\\pi_{A} R \\ltimes S',
            Join(
                operator=JoinOperator.SEMI,
                left=Relation('R').project('A'),
                right=Relation('S'),
            ),
        ),
        # Test multiple projections
        (
            '\\pi_{A} \\pi_{B} R',
            Relation('R').project('B', optimise=False).project('A', optimise=False),
        ),
        # Test projection with complex set operations
        (
            '\\pi_{A} (R \\cup S) - \\pi_{B} (T \\cap U)',
            SetOperation(
                operator=SetOperator.DIFFERENCE,
                left=Relation('R').union('S').project('A'),
                right=Relation('T').intersect('U').project('B'),
            ),
        ),
        # Test theta join precedence
        (
            'R \\overset{A = B}{\\bowtie} S - T',
            SetOperation(
                operator=SetOperator.DIFFERENCE,
                left=Relation('R').theta_join('S', EQ(attribute('A'), attribute('B'))),
                right=Relation('T'),
            ),
        ),
        # Test projection with theta join
        (
            '\\pi_{A,B} (R \\overset{C = D}{\\bowtie} S)',
            Relation('R')
            .theta_join(
                'S',
                EQ(attribute('C'), attribute('D')),
            )
            .project(['A', 'B']),
        ),
    ],
)
def test_operator_precedence(query: str, expected: RAQuery) -> None:
    """Test that the grammar correctly handles operator precedence."""
    assert parse_ra(query) == expected
