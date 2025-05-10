import pytest
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.ast import (
    Attribute,
    Comparison,
    ComparisonOperator,
    Division,
    Join,
    JoinOperator,
    Projection,
    RAQuery,
    Relation,
    SetOperation,
    SetOperator,
    ThetaJoin,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        # Test basic projection precedence
        (
            '\\pi_{A} R - \\pi_{A} S',
            SetOperation(
                operator=SetOperator.DIFFERENCE,
                left=Projection(
                    attributes=[Attribute('A')],
                    subquery=Relation('R'),
                ),
                right=Projection(
                    attributes=[Attribute('A')],
                    subquery=Relation('S'),
                ),
            ),
        ),
        # Test parenthesized expressions
        (
            '\\pi_{A} (R - S)',
            Projection(
                attributes=[Attribute('A')],
                subquery=SetOperation(
                    operator=SetOperator.DIFFERENCE,
                    left=Relation('R'),
                    right=Relation('S'),
                ),
            ),
        ),
        # Test operator associativity (left-to-right)
        (
            'R \\cup S - T',
            SetOperation(
                operator=SetOperator.DIFFERENCE,
                left=SetOperation(
                    operator=SetOperator.UNION,
                    left=Relation('R'),
                    right=Relation('S'),
                ),
                right=Relation('T'),
            ),
        ),
        # Test join precedence with set operations
        (
            'R \\Join S - T \\Join U',
            SetOperation(
                operator=SetOperator.DIFFERENCE,
                left=Join(
                    operator=JoinOperator.NATURAL,
                    left=Relation('R'),
                    right=Relation('S'),
                ),
                right=Join(
                    operator=JoinOperator.NATURAL,
                    left=Relation('T'),
                    right=Relation('U'),
                ),
            ),
        ),
        # Test operator precedence mix
        (
            'R \\cap S \\cup T',
            SetOperation(
                operator=SetOperator.UNION,
                left=SetOperation(
                    operator=SetOperator.INTERSECT,
                    left=Relation('R'),
                    right=Relation('S'),
                ),
                right=Relation('T'),
            ),
        ),
        # Test projection vs set operation precedence
        (
            '\\pi_{A,B} R \\cup \\pi_{C,D} S',
            SetOperation(
                operator=SetOperator.UNION,
                left=Projection(
                    attributes=[Attribute('A'), Attribute('B')],
                    subquery=Relation('R'),
                ),
                right=Projection(
                    attributes=[Attribute('C'), Attribute('D')],
                    subquery=Relation('S'),
                ),
            ),
        ),
        # Test division with other operators
        (
            'R \\div S \\times T',
            SetOperation(
                operator=SetOperator.CARTESIAN,
                left=Division(
                    dividend=Relation('R'),
                    divisor=Relation('S'),
                ),
                right=Relation('T'),
            ),
        ),
        # Test semi-join with projection
        (
            '\\pi_{A} R \\ltimes S',
            Join(
                operator=JoinOperator.SEMI,
                left=Projection(
                    attributes=[Attribute('A')],
                    subquery=Relation('R'),
                ),
                right=Relation('S'),
            ),
        ),
        # Test multiple projections
        (
            '\\pi_{A} \\pi_{B} R',
            Projection(
                attributes=[Attribute('A')],
                subquery=Projection(
                    attributes=[Attribute('B')],
                    subquery=Relation('R'),
                ),
            ),
        ),
        # Test projection with complex set operations
        (
            '\\pi_{A} (R \\cup S) - \\pi_{B} (T \\cap U)',
            SetOperation(
                operator=SetOperator.DIFFERENCE,
                left=Projection(
                    attributes=[Attribute('A')],
                    subquery=SetOperation(
                        operator=SetOperator.UNION,
                        left=Relation('R'),
                        right=Relation('S'),
                    ),
                ),
                right=Projection(
                    attributes=[Attribute('B')],
                    subquery=SetOperation(
                        operator=SetOperator.INTERSECT,
                        left=Relation('T'),
                        right=Relation('U'),
                    ),
                ),
            ),
        ),
        # Test theta join precedence
        (
            'R \\overset{A = B}{\\bowtie} S - T',
            SetOperation(
                operator=SetOperator.DIFFERENCE,
                left=ThetaJoin(
                    left=Relation('R'),
                    right=Relation('S'),
                    condition=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute('A'),
                        right=Attribute('B'),
                    ),
                ),
                right=Relation('T'),
            ),
        ),
        # Test projection with theta join
        (
            '\\pi_{A,B} (R \\overset{C = D}{\\bowtie} S)',
            Projection(
                attributes=[Attribute('A'), Attribute('B')],
                subquery=ThetaJoin(
                    left=Relation('R'),
                    right=Relation('S'),
                    condition=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute('C'),
                        right=Attribute('D'),
                    ),
                ),
            ),
        ),
    ],
)
def test_operator_precedence(query: str, expected: RAQuery) -> None:
    """Test that the grammar correctly handles operator precedence."""
    assert parse_ra(query) == expected
