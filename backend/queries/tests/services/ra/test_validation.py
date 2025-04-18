from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from databases.models.database_connection_info import DatabaseConnectionInfo
from databases.types import DataType
from queries.services.ra.validation import validate_ra


@pytest.fixture(autouse=True)
def mock_get_schema() -> Generator[MagicMock, None, None]:
    with patch('queries.services.ra.validation.validate.get_schema') as mock:
        mock.return_value = {
            'R': {
                'A': DataType.INTEGER,
                'B': DataType.STRING,
                'C': DataType.FLOAT,
            },
            'S': {
                'D': DataType.INTEGER,
                'E': DataType.STRING,
                'F': DataType.FLOAT,
            },
            'T': {
                'A': DataType.INTEGER,  # Same name as R.A
                'G': DataType.STRING,
                'H': DataType.BOOLEAN,
            },
            'Employee': {
                'id': DataType.INTEGER,
                'name': DataType.STRING,
                'department': DataType.STRING,
                'salary': DataType.FLOAT,
            },
            'Department': {
                'id': DataType.INTEGER,
                'name': DataType.STRING,
                'manager_id': DataType.INTEGER,
            },
        }
        yield mock


mock_db = DatabaseConnectionInfo(
    database_type='sqlite',
    host='',
    port=None,
    name='test_db',
    user=None,
    password=None,
)


class TestRAValidation:
    @pytest.mark.parametrize('query', [
        'R',  # Simple relation
        '\\pi_{A, B} R',  # Projection with valid attributes
        '\\sigma_{A > 10} R',  # Selection with valid condition
        'R \\Join S',  # Natural join
        'R \\times S',  # Cartesian product
        'R \\cup S',  # Union
        'R \\cap S',  # Intersection
        'R - S',  # Difference
        '\\Gamma_{((A), ((B, count, X)))} R',  # Aggregation
        '\\operatorname{T}_{(10, A)} R',  # Top N
        'Employee \\overset{Employee.department = Department.name}{\\bowtie} Department',  # Theta join
        '\\pi_{A, B} (\\sigma_{C > 5.0} R)',  # Nested operations
    ])
    def test_valid_queries(self, query: str) -> None:
        result = validate_ra(query, mock_db)
        assert result['valid'], f'Query should be valid: {query}, but got errors: {result['errors']}'

    @pytest.mark.parametrize(
        'query, expected_error_message',
        [
            # Unknown relation
            ('X', 'Unknown relation: X'),
            ('R \\Join X', 'Unknown relation: X'),
            # Unknown attributes
            ('\\pi_{Z} R', 'Unknown attribute: Z'),
            ('\\sigma_{Z > 10} R', 'Unknown attribute: Z'),
            # Join condition errors
            ('R \\overset{A = G}{\\bowtie} S', 'Unknown attribute: G'),
            # Aggregation errors
            ('\\Gamma_{((Z), ((A, sum, X)))} R', 'Unknown attribute: Z'),
            ('\\Gamma_{((A), ((Z, sum, X)))} R', 'Unknown attribute: Z'),
            # TopN errors
            ('\\operatorname{T}_{(10, Z)} R', 'Unknown attribute: Z'),
        ],
    )
    def test_semantic_errors(self, query: str, expected_error_message: str) -> None:
        """Test that semantic errors are correctly identified."""
        result = validate_ra(query, mock_db)
        assert not result['valid'], f'Query should be invalid: {query}'
        assert any(
            expected_error_message in error['message'] for error in result['errors']
        ), f"Expected error '{expected_error_message}' not found in {result['errors']}"

    @pytest.mark.parametrize('query', [
        # Complex nested query with various operations
        # '\\pi_{name, salary} (\\sigma_{department = \\"IT\\" \\land salary > 50000} Employee)',
        # Query with nested joins
        '\\pi_{Employee.name, Department.name} (Employee \\Join Department)',
        # Query with aggregation and filtering
        '\\pi_{department, avg_salary} (\\Gamma_{((department), ((salary, avg, \\text{avg_salary})))} (\\sigma_{salary > 30000} Employee))',
        # Complex query with multiple operations
        '\\pi_{department, count} (\\Gamma_{((department), ((id, count, count)))} (\\sigma_{salary > 50000} Employee))',
    ])
    def test_complex_query_validation(self, query) -> None:
        result = validate_ra(query, mock_db)
        assert result[
            'valid'
        ], f'Complex query should be valid: {query}, but got errors: {result['errors']}'

    @pytest.mark.parametrize(
        'query, expected_error_message',
        [
            # Ambiguous attributes in natural joins
            ('R \\overset{A = B}{\\bowtie} T', 'Ambiguous attribute: A in relations: R, T'),
        ],
    )
    def test_ambiguous_attribute_errors(self, query: str, expected_error_message: str) -> None:
        """Test detection of ambiguous attribute references."""
        result = validate_ra(query, mock_db)
        assert not result['valid'], f'Query should be invalid due to ambiguity: {query}'
        assert any(
            expected_error_message in error['message'] for error in result['errors']
        ), f"Expected error '{expected_error_message}' not found in {result['errors']}"

