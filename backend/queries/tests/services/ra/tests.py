import pytest
from queries.services.ra.ast import (
    AggregationFunction,
    Attribute,
    Comparison,
    ComparisonOperator,
    Division,
    GroupedAggregation,
    Join,
    JoinOperator,
    Projection,
    Relation,
    Selection,
    SetOperation,
    SetOperator,
    ThetaJoin,
    TopN,
)
from queries.services.ra.parser import parse_ra


def test_relation() -> None:
    relation = parse_ra('Sailor')
    assert isinstance(relation, Relation)
    assert relation.name == 'Sailor'


def test_qualified_attribute() -> None:
    projection = parse_ra('\\pi_{Sailor.sname} Sailor')
    assert isinstance(projection, Projection)
    assert projection.attributes[0].relation == 'Sailor'


def test_projection() -> None:
    projection = parse_ra('\\pi_{a,b,c} R')
    assert isinstance(projection, Projection)
    assert [a.name for a in projection.attributes] == ['a', 'b', 'c']
    assert isinstance(projection.expression, Relation)


def test_selection() -> None:
    selection = parse_ra('\\sigma_{a = 5} R')
    assert isinstance(selection, Selection)
    assert isinstance(selection.condition, Comparison)
    assert selection.condition.operator == ComparisonOperator.EQUAL
    assert isinstance(selection.condition.left, Attribute)
    assert selection.condition.right == 5


@pytest.mark.parametrize(
    'query, expected_operator',
    [
        ('R \\cup S', SetOperator.UNION),
        ('R - S', SetOperator.DIFFERENCE),
        ('R \\cap S', SetOperator.INTERSECT),
        ('R \\times S', SetOperator.CARTESIAN),
    ],
)
def test_set_operations(query: str, expected_operator: SetOperator) -> None:
    set_operation = parse_ra(query)
    assert isinstance(set_operation, SetOperation)
    assert set_operation.operator == expected_operator


@pytest.mark.parametrize(
    'query, expected_operator',
    [
        ('R \\Join S', JoinOperator.NATURAL),
        ('R \\ltimes S', JoinOperator.SEMI),
    ],
)
def test_joins(query: str, expected_operator: JoinOperator) -> None:
    join = parse_ra(query)
    assert isinstance(join, Join)
    assert join.operator == expected_operator


def test_theta_join() -> None:
    query = 'R \\overset{a = b}{\\bowtie} S'
    theta_join = parse_ra(query)
    assert isinstance(theta_join, ThetaJoin)
    assert isinstance(theta_join.condition, Comparison)


def test_division() -> None:
    query = 'R \\div S'
    division = parse_ra(query)
    assert isinstance(division, Division)
    assert isinstance(division.dividend, Relation)
    assert isinstance(division.divisor, Relation)
    assert division.dividend.name == 'R'
    assert division.divisor.name == 'S'


def test_grouped_aggregation() -> None:
    query = '\\Gamma_{((a,b),((c,avg,x)))} R'
    tree = parse_ra(query)
    assert isinstance(tree, GroupedAggregation)
    assert [g.name for g in tree.group_by] == ['a', 'b']
    aggregation = tree.aggregations[0]
    assert aggregation.aggregation_function == AggregationFunction.AVG
    assert aggregation.input.name == 'c'
    assert aggregation.output == 'x'


def test_topn() -> None:
    tree = parse_ra('T_{(5,score)} R')
    assert isinstance(tree, TopN)
    assert tree.limit == 5
    assert tree.attribute.name == 'score'


def test_nested_expr() -> None:
    query = '\\pi_{sname} (\\sigma_{color = "red"} Boat)'
    tree = parse_ra(query)
    assert isinstance(tree, Projection)
    assert isinstance(tree.expression, Selection)
