import pytest
from queries.services.ra.ast import (
    AggregationFunction,
    Attribute,
    BinaryBooleanExpression,
    BinaryBooleanOperator,
    Comparison,
    ComparisonOperator,
    Division,
    GroupedAggregation,
    Join,
    JoinOperator,
    NotExpression,
    Projection,
    Relation,
    Selection,
    SetOperation,
    SetOperator,
    ThetaJoin,
    TopN,
)
from queries.services.ra.parser import parse_ra


class TestRelationAndAttributes:
    def test_simple_relation(self) -> None:
        relation = parse_ra('Sailor')
        assert isinstance(relation, Relation)
        assert relation.name == 'Sailor'
        assert relation.attributes == []

    def test_relations_with_special_chars(self) -> None:
        relation = parse_ra('\\text{Student_2023}')
        assert isinstance(relation, Relation)
        assert relation.name == 'Student_2023'

    def test_qualified_attribute(self) -> None:
        projection = parse_ra('\\pi_{Sailor.sname} Sailor')
        assert isinstance(projection, Projection)
        assert projection.attributes[0].relation == 'Sailor'
        assert projection.attributes[0].name == 'sname'

    def test_multiple_qualified_attributes(self) -> None:
        projection = parse_ra('\\pi_{Boat.bid, Sailor.sid, Sailor.sname} (Boat \\Join Sailor)')
        assert isinstance(projection, Projection)
        assert len(projection.attributes) == 3
        assert projection.attributes[0].relation == 'Boat'
        assert projection.attributes[0].name == 'bid'
        assert projection.attributes[1].relation == 'Sailor'
        assert projection.attributes[1].name == 'sid'
        assert projection.attributes[2].relation == 'Sailor'
        assert projection.attributes[2].name == 'sname'


class TestProjection:
    def test_simple_projection(self) -> None:
        projection = parse_ra('\\pi_{a,b,c} R')
        assert isinstance(projection, Projection)
        assert [a.name for a in projection.attributes] == ['a', 'b', 'c']
        assert isinstance(projection.expression, Relation)
        assert projection.expression.name == 'R'

    def test_projection_with_single_attribute(self) -> None:
        projection = parse_ra('\\pi_{name} Employee')
        assert isinstance(projection, Projection)
        assert len(projection.attributes) == 1
        assert projection.attributes[0].name == 'name'


class TestComparison:
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
    def test_comparison_operators(self, op_str: str, expected_op: ComparisonOperator) -> None:
        # Use selection as a wrapper to test comparison expressions
        selection = parse_ra(f'\\sigma_{{a {op_str} 5}} R')
        assert isinstance(selection, Selection)
        assert isinstance(selection, Selection)
        assert isinstance(selection.condition, Comparison)
        assert selection.condition.operator == expected_op

    def test_attribute_to_number_comparison(self) -> None:
        selection = parse_ra('\\sigma_{salary > 50000} Employee')
        assert isinstance(selection, Selection)
        assert isinstance(selection.condition, Comparison)
        assert selection.condition.operator == ComparisonOperator.GREATER_THAN
        assert isinstance(selection.condition.left, Attribute)
        assert selection.condition.left.name == 'salary'
        assert selection.condition.right == 50000

    def test_attribute_to_string_comparison(self) -> None:
        selection = parse_ra('\\sigma_{name = "John"} Employee')
        assert isinstance(selection, Selection)
        assert isinstance(selection.condition, Comparison)
        assert selection.condition.operator == ComparisonOperator.EQUAL
        assert isinstance(selection.condition.left, Attribute)
        assert selection.condition.left.name == 'name'
        assert selection.condition.right == 'John'

    def test_attribute_to_attribute_comparison(self) -> None:
        selection = parse_ra(
            '\\sigma_{Employee.salary > Department.budget} (Employee \\Join Department)'
        )
        assert isinstance(selection, Selection)
        assert isinstance(selection.condition, Comparison)
        assert selection.condition.operator == ComparisonOperator.GREATER_THAN
        assert isinstance(selection.condition.left, Attribute)
        assert selection.condition.left.relation == 'Employee'
        assert selection.condition.left.name == 'salary'
        assert isinstance(selection.condition.right, Attribute)
        assert selection.condition.right.relation == 'Department'
        assert selection.condition.right.name == 'budget'


class TestBooleanExpressions:
    def test_and_expression(self) -> None:
        selection = parse_ra('\\sigma_{a = 5 \\land b = 10} R')
        assert isinstance(selection, Selection)
        expr = selection.condition
        assert isinstance(expr, BinaryBooleanExpression)
        assert expr.operator == BinaryBooleanOperator.AND

        left = expr.left
        assert isinstance(left, Comparison)
        assert left.operator == ComparisonOperator.EQUAL
        assert isinstance(left.left, Attribute)
        assert left.left.name == 'a'
        assert left.right == 5

        right = expr.right
        assert isinstance(right, Comparison)
        assert right.operator == ComparisonOperator.EQUAL
        assert isinstance(right.left, Attribute)
        assert right.left.name == 'b'
        assert right.right == 10

    def test_or_expression(self) -> None:
        selection = parse_ra('\\sigma_{a = 5 \\lor b = 10} R')
        assert isinstance(selection, Selection)
        expr = selection.condition
        assert isinstance(expr, BinaryBooleanExpression)
        assert expr.operator == BinaryBooleanOperator.OR

        left = expr.left
        assert isinstance(left, Comparison)
        assert left.operator == ComparisonOperator.EQUAL
        assert isinstance(left.left, Attribute)
        assert left.left.name == 'a'
        assert left.right == 5

        right = expr.right
        assert isinstance(right, Comparison)
        assert right.operator == ComparisonOperator.EQUAL
        assert isinstance(right.left, Attribute)
        assert right.left.name == 'b'
        assert right.right == 10

    def test_not_expression(self) -> None:
        selection = parse_ra('\\sigma_{\\lnot (a = 5)} R')
        assert isinstance(selection, Selection)
        expr = selection.condition
        assert isinstance(expr, NotExpression)
        inner_condition = expr.expression
        assert isinstance(inner_condition, Comparison)
        assert inner_condition.operator == ComparisonOperator.EQUAL
        assert isinstance(inner_condition.left, Attribute)
        assert inner_condition.left.name == 'a'
        assert inner_condition.right == 5

    def test_nested_boolean_expressions(self) -> None:
        selection = parse_ra('\\sigma_{(a = 5 \\land b > 10) \\lor c = "test"} R')
        assert isinstance(selection, Selection)
        expr = selection.condition
        assert isinstance(expr, BinaryBooleanExpression)
        assert expr.operator == BinaryBooleanOperator.OR

        left = expr.left
        assert isinstance(left, BinaryBooleanExpression)
        assert left.operator == BinaryBooleanOperator.AND

        right = expr.right
        assert isinstance(right, Comparison)
        assert right.operator == ComparisonOperator.EQUAL
        assert isinstance(right.left, Attribute)
        assert right.left.name == 'c'
        assert right.right == 'test'

    def test_complex_expression_with_not(self) -> None:
        selection = parse_ra('\\sigma_{\\lnot (a = 5 \\lor b = 10) \\land c > 20} R')
        assert isinstance(selection, Selection)
        expr = selection.condition
        assert isinstance(expr, BinaryBooleanExpression)
        assert expr.operator == BinaryBooleanOperator.AND

        left = expr.left
        assert isinstance(left, NotExpression)
        not_inner = left.expression
        assert isinstance(not_inner, BinaryBooleanExpression)
        assert not_inner.operator == BinaryBooleanOperator.OR

        right = expr.right
        assert isinstance(right, Comparison)
        assert right.operator == ComparisonOperator.GREATER_THAN
        assert isinstance(right.left, Attribute)
        assert right.left.name == 'c'
        assert right.right == 20

    def test_precedence_and_over_or(self) -> None:
        # Test that AND has higher precedence than OR
        selection = parse_ra('\\sigma_{a = 1 \\lor b = 2 \\land c = 3} R')
        assert isinstance(selection, Selection)
        expr = selection.condition
        assert isinstance(expr, BinaryBooleanExpression)
        assert expr.operator == BinaryBooleanOperator.OR

        left = expr.left
        assert isinstance(left, Comparison)
        assert left.operator == ComparisonOperator.EQUAL
        assert isinstance(left.left, Attribute)
        assert left.left.name == 'a'
        assert left.right == 1

        right = expr.right
        assert isinstance(right, BinaryBooleanExpression)
        assert right.operator == BinaryBooleanOperator.AND

        assert isinstance(right.left, Comparison)
        assert isinstance(right.left.left, Attribute)
        assert right.left.left.name == 'b'

        assert isinstance(right.right, Comparison)
        assert isinstance(right.right.left, Attribute)
        assert right.right.left.name == 'c'


class TestSelection:
    def test_simple_selection(self) -> None:
        selection = parse_ra('\\sigma_{a = 5} R')
        assert isinstance(selection, Selection)
        assert isinstance(selection, Selection)
        assert isinstance(selection.condition, Comparison)
        assert selection.condition.operator == ComparisonOperator.EQUAL
        assert isinstance(selection.condition.left, Attribute)
        assert selection.condition.left.name == 'a'
        assert selection.condition.right == 5
        assert isinstance(selection.expression, Relation)
        assert selection.expression.name == 'R'


class TestSetOperations:
    @pytest.mark.parametrize(
        'query, expected_operator',
        [
            ('R \\cup S', SetOperator.UNION),
            ('R - S', SetOperator.DIFFERENCE),
            ('R \\cap S', SetOperator.INTERSECT),
            ('R \\times S', SetOperator.CARTESIAN),
        ],
    )
    def test_basic_set_operations(self, query: str, expected_operator: SetOperator) -> None:
        set_operation = parse_ra(query)
        assert isinstance(set_operation, SetOperation)
        assert set_operation.operator == expected_operator
        assert isinstance(set_operation.left, Relation)
        assert set_operation.left.name == 'R'
        assert isinstance(set_operation.right, Relation)
        assert set_operation.right.name == 'S'

    def test_nested_set_operations(self) -> None:
        query = 'R \\cup (S - T)'
        set_operation = parse_ra(query)
        assert isinstance(set_operation, SetOperation)
        assert set_operation.operator == SetOperator.UNION
        assert isinstance(set_operation.left, Relation)
        assert set_operation.left.name == 'R'

        inner_operation = set_operation.right
        assert isinstance(inner_operation, SetOperation)
        assert inner_operation.operator == SetOperator.DIFFERENCE
        assert isinstance(inner_operation.left, Relation)
        assert inner_operation.left.name == 'S'
        assert isinstance(inner_operation.right, Relation)
        assert inner_operation.right.name == 'T'


class TestJoins:
    @pytest.mark.parametrize(
        'query, expected_operator',
        [
            ('R \\Join S', JoinOperator.NATURAL),
            ('R \\ltimes S', JoinOperator.SEMI),
        ],
    )
    def test_basic_joins(self, query: str, expected_operator: JoinOperator) -> None:
        join = parse_ra(query)
        assert isinstance(join, Join)
        assert join.operator == expected_operator
        assert isinstance(join.left, Relation)
        assert join.left.name == 'R'
        assert isinstance(join.right, Relation)
        assert join.right.name == 'S'

    def test_theta_join_equality(self) -> None:
        query = 'R \\overset{a = b}{\\bowtie} S'
        theta_join = parse_ra(query)
        assert isinstance(theta_join, ThetaJoin)
        assert isinstance(theta_join.condition, Comparison)
        assert theta_join.condition.operator == ComparisonOperator.EQUAL
        assert isinstance(theta_join.condition.left, Attribute)
        assert theta_join.condition.left.name == 'a'
        assert isinstance(theta_join.condition.right, Attribute)
        assert theta_join.condition.right.name == 'b'
        assert isinstance(theta_join.left, Relation)
        assert theta_join.left.name == 'R'
        assert isinstance(theta_join.right, Relation)
        assert theta_join.right.name == 'S'

    def test_theta_join_complex_condition(self) -> None:
        query = 'R \\overset{a > b \\land c = d}{\\bowtie} S'
        theta_join = parse_ra(query)
        assert isinstance(theta_join, ThetaJoin)
        assert isinstance(theta_join.condition, BinaryBooleanExpression)
        assert theta_join.condition.operator == BinaryBooleanOperator.AND

        left_cond = theta_join.condition.left
        assert isinstance(left_cond, Comparison)
        assert left_cond.operator == ComparisonOperator.GREATER_THAN
        assert isinstance(left_cond.left, Attribute)
        assert left_cond.left.name == 'a'
        assert isinstance(left_cond.right, Attribute)
        assert left_cond.right.name == 'b'

        right_cond = theta_join.condition.right
        assert isinstance(right_cond, Comparison)
        assert right_cond.operator == ComparisonOperator.EQUAL
        assert isinstance(right_cond.left, Attribute)
        assert right_cond.left.name == 'c'
        assert isinstance(right_cond.right, Attribute)
        assert right_cond.right.name == 'd'

    def test_nested_joins(self) -> None:
        query = 'R \\Join (S \\Join T)'
        join = parse_ra(query)
        assert isinstance(join, Join)
        assert join.operator == JoinOperator.NATURAL
        assert isinstance(join.left, Relation)
        assert join.left.name == 'R'

        inner_join = join.right
        assert isinstance(inner_join, Join)
        assert inner_join.operator == JoinOperator.NATURAL
        assert isinstance(inner_join.left, Relation)
        assert inner_join.left.name == 'S'
        assert isinstance(inner_join.right, Relation)
        assert inner_join.right.name == 'T'

    def test_join_chaining(self) -> None:
        # Test associativity of joins
        query = 'R \\Join S \\Join T'
        join = parse_ra(query)
        assert isinstance(join, Join)
        assert join.operator == JoinOperator.NATURAL

        # The exact structure depends on whether the grammar makes joins left- or right-associative
        # We'll check both possibilities
        if isinstance(join.left, Join):
            # Left-associative: (R ⋈ S) ⋈ T
            assert isinstance(join.left, Join)
            assert join.left.operator == JoinOperator.NATURAL
            assert isinstance(join.left.left, Relation)
            assert join.left.left.name == 'R'
            assert isinstance(join.left.right, Relation)
            assert join.left.right.name == 'S'
            assert isinstance(join.right, Relation)
            assert join.right.name == 'T'
        else:
            # Right-associative: R ⋈ (S ⋈ T)
            assert isinstance(join.left, Relation)
            assert join.left.name == 'R'
            assert isinstance(join.right, Join)
            assert join.right.operator == JoinOperator.NATURAL
            assert isinstance(join.right.left, Relation)
            assert join.right.left.name == 'S'
            assert isinstance(join.right.right, Relation)
            assert join.right.right.name == 'T'


class TestDivision:
    def test_simple_division(self) -> None:
        query = 'R \\div S'
        division = parse_ra(query)
        assert isinstance(division, Division)
        assert isinstance(division.dividend, Relation)
        assert isinstance(division.divisor, Relation)
        assert division.dividend.name == 'R'
        assert division.divisor.name == 'S'

    def test_complex_division(self) -> None:
        query = '(\\pi_{x,y} R) \\div (\\pi_{y} S)'
        division = parse_ra(query)
        assert isinstance(division, Division)
        assert isinstance(division.dividend, Projection)
        assert len(division.dividend.attributes) == 2
        assert [a.name for a in division.dividend.attributes] == ['x', 'y']

        assert isinstance(division.divisor, Projection)
        assert len(division.divisor.attributes) == 1
        assert division.divisor.attributes[0].name == 'y'


class TestGroupedAggregation:
    def test_simple_aggregation(self) -> None:
        query = '\\Gamma_{((a,b),((c,avg,x)))} R'
        tree = parse_ra(query)
        assert isinstance(tree, GroupedAggregation)
        assert len(tree.group_by) == 2
        assert [g.name for g in tree.group_by] == ['a', 'b']
        assert len(tree.aggregations) == 1

        aggregation = tree.aggregations[0]
        assert aggregation.aggregation_function == AggregationFunction.AVG
        assert aggregation.input.name == 'c'
        assert aggregation.output == 'x'

        assert isinstance(tree.expression, Relation)
        assert tree.expression.name == 'R'

    def test_multiple_aggregations(self) -> None:
        query = '\\Gamma_{((deptno),((salary,avg,\\text{avg_sal}),(salary,max,\\text{max_sal}),(salary,min,\\text{min_sal})))} Employee'
        tree = parse_ra(query)
        assert isinstance(tree, GroupedAggregation)
        assert len(tree.group_by) == 1
        assert tree.group_by[0].name == 'deptno'
        assert len(tree.aggregations) == 3

        agg_functions = [agg.aggregation_function for agg in tree.aggregations]
        agg_inputs = [agg.input.name for agg in tree.aggregations]
        agg_outputs = [agg.output for agg in tree.aggregations]

        assert agg_functions == [
            AggregationFunction.AVG,
            AggregationFunction.MAX,
            AggregationFunction.MIN,
        ]
        assert all(input_name == 'salary' for input_name in agg_inputs)
        assert agg_outputs == ['avg_sal', 'max_sal', 'min_sal']

    @pytest.mark.parametrize(
        'agg_function_str, expected_function',
        [
            ('count', AggregationFunction.COUNT),
            ('sum', AggregationFunction.SUM),
            ('avg', AggregationFunction.AVG),
            ('min', AggregationFunction.MIN),
            ('max', AggregationFunction.MAX),
        ],
    )
    def test_aggregation_functions(
        self, agg_function_str: str, expected_function: AggregationFunction
    ) -> None:
        query = '\\Gamma_{((dept),((' + f'in,{agg_function_str},out' + ')))} Employee'
        tree = parse_ra(query)
        assert isinstance(tree, GroupedAggregation)
        assert len(tree.aggregations) == 1
        assert tree.aggregations[0].aggregation_function == expected_function

    def test_aggregation_without_grouping(self) -> None:
        query = '\\Gamma_{((),((salary,avg,\\text{avg_sal})))} Employee'
        tree = parse_ra(query)
        assert isinstance(tree, GroupedAggregation)
        assert len(tree.group_by) == 0
        assert len(tree.aggregations) == 1
        assert tree.aggregations[0].aggregation_function == AggregationFunction.AVG
        assert tree.aggregations[0].input.name == 'salary'
        assert tree.aggregations[0].output == 'avg_sal'


class TestTopN:
    def test_simple_topn(self) -> None:
        tree = parse_ra('\operatorname{Top}_{(5,score)} R')
        assert isinstance(tree, TopN)
        assert tree.limit == 5
        assert tree.attribute.name == 'score'
        assert isinstance(tree.expression, Relation)
        assert tree.expression.name == 'R'

    def test_topn_with_larger_limit(self) -> None:
        tree = parse_ra('\operatorname{Top}_{(100,salary)} Employee')
        assert isinstance(tree, TopN)
        assert tree.limit == 100
        assert tree.attribute.name == 'salary'

    def test_topn_over_complex_expression(self) -> None:
        tree = parse_ra('\operatorname{Top}_{(10,price)} (\\sigma_{category = "electronics"} Products)')
        assert isinstance(tree, TopN)
        assert tree.limit == 10
        assert tree.attribute.name == 'price'
        assert isinstance(tree.expression, Selection)


class TestComplexQueries:
    def test_projection_over_selection(self) -> None:
        query = '\\pi_{sname} (\\sigma_{color = "red"} Boat)'
        tree = parse_ra(query)
        assert isinstance(tree, Projection)
        assert len(tree.attributes) == 1
        assert tree.attributes[0].name == 'sname'
        assert isinstance(tree.expression, Selection)
        assert isinstance(tree.expression.condition, Comparison)
        assert tree.expression.condition.right == 'red'

    def test_selection_over_join(self) -> None:
        query = '\\sigma_{Sailor.rating > 7} (Sailor \\Join Boat)'
        tree = parse_ra(query)
        assert isinstance(tree, Selection)
        assert isinstance(tree.condition, Comparison)
        assert tree.condition.operator == ComparisonOperator.GREATER_THAN
        assert isinstance(tree.condition.left, Attribute)
        assert tree.condition.left.relation == 'Sailor'
        assert tree.condition.left.name == 'rating'
        assert tree.condition.right == 7
        assert isinstance(tree.expression, Join)

    def test_projection_over_theta_join(self) -> None:
        query = '\\pi_{name, title} (Employee \\overset{Employee.deptno = Department.deptno}{\\bowtie} Department)'
        tree = parse_ra(query)
        assert isinstance(tree, Projection)
        assert len(tree.attributes) == 2
        assert [a.name for a in tree.attributes] == ['name', 'title']
        assert isinstance(tree.expression, ThetaJoin)
        assert isinstance(tree.expression.condition, Comparison)

    def test_aggregation_with_projection_and_selection(self) -> None:
        query = """\\Gamma_{((deptno),((salary,avg,\\text{avg_sal})))} (\\pi_{deptno, salary} (\\sigma_{location = "HQ"} Employee))"""
        tree = parse_ra(query)
        assert isinstance(tree, GroupedAggregation)
        assert len(tree.group_by) == 1
        assert tree.group_by[0].name == 'deptno'
        assert len(tree.aggregations) == 1
        assert isinstance(tree.expression, Projection)
        assert isinstance(tree.expression.expression, Selection)

    def test_complex_query_with_multiple_operations(self) -> None:
        query = """\\pi_{name, \\text{dept_name}} (Employee \\overset{Employee.deptno = Department.deptno}{\\bowtie} (\\sigma_{budget > 100000} Department))"""
        tree = parse_ra(query)
        assert isinstance(tree, Projection)
        assert len(tree.attributes) == 2
        assert [a.name for a in tree.attributes] == ['name', 'dept_name']
        assert isinstance(tree.expression, ThetaJoin)
        assert isinstance(tree.expression.right, Selection)
