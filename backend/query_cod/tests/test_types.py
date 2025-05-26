import pytest
from query_cod.types import DataType


ALL_DATATYPES = list(DataType)
NUMERIC_DATATYPES = {t for t in ALL_DATATYPES if t.is_numeric()}
STRING_DATATYPES = {t for t in ALL_DATATYPES if t.is_string()}

NUMERIC_DATATYPE_PAIRS = [(s, t) for s in NUMERIC_DATATYPES for t in NUMERIC_DATATYPES]
STRING_DATATYPE_PAIRS = [(s, t) for s in STRING_DATATYPES for t in STRING_DATATYPES]

ALL_CAST_PAIRS: set[tuple[DataType, DataType]] = {
    (s, t) for s in ALL_DATATYPES for t in ALL_DATATYPES if t != DataType.NULL
}

NULL_CAST_PAIRS = [(DataType.NULL, t) for t in ALL_DATATYPES if t != DataType.NULL]

VALID_CASTS: list[tuple[DataType, DataType]] = (
    NUMERIC_DATATYPE_PAIRS
    + STRING_DATATYPE_PAIRS
    + NULL_CAST_PAIRS
    + [
        # Numeric type casts
        (DataType.SMALLINT, DataType.VARCHAR),
        (DataType.SMALLINT, DataType.CHAR),
        (DataType.INTEGER, DataType.VARCHAR),
        (DataType.INTEGER, DataType.CHAR),
        (DataType.DECIMAL, DataType.VARCHAR),
        (DataType.DECIMAL, DataType.CHAR),
        (DataType.NUMERIC, DataType.VARCHAR),
        (DataType.NUMERIC, DataType.CHAR),
        (DataType.REAL, DataType.VARCHAR),
        (DataType.REAL, DataType.CHAR),
        (DataType.DOUBLE_PRECISION, DataType.VARCHAR),
        (DataType.DOUBLE_PRECISION, DataType.CHAR),
        (DataType.FLOAT, DataType.VARCHAR),
        (DataType.FLOAT, DataType.CHAR),
        (DataType.DOUBLE_PRECISION, DataType.VARCHAR),
        (DataType.DOUBLE_PRECISION, DataType.CHAR),
        # String type casts
        (DataType.CHAR, DataType.SMALLINT),
        (DataType.CHAR, DataType.INTEGER),
        (DataType.CHAR, DataType.DECIMAL),
        (DataType.CHAR, DataType.NUMERIC),
        (DataType.CHAR, DataType.REAL),
        (DataType.CHAR, DataType.FLOAT),
        (DataType.CHAR, DataType.DOUBLE_PRECISION),
        (DataType.CHAR, DataType.DATE),
        (DataType.CHAR, DataType.TIME),
        (DataType.CHAR, DataType.TIMESTAMP),
        (DataType.CHAR, DataType.BIT),
        (DataType.CHAR, DataType.BIT_VARYING),
        (DataType.CHAR, DataType.BOOLEAN),
        (DataType.VARCHAR, DataType.SMALLINT),
        (DataType.VARCHAR, DataType.INTEGER),
        (DataType.VARCHAR, DataType.DECIMAL),
        (DataType.VARCHAR, DataType.NUMERIC),
        (DataType.VARCHAR, DataType.REAL),
        (DataType.VARCHAR, DataType.FLOAT),
        (DataType.VARCHAR, DataType.DOUBLE_PRECISION),
        (DataType.VARCHAR, DataType.DATE),
        (DataType.VARCHAR, DataType.TIME),
        (DataType.VARCHAR, DataType.TIMESTAMP),
        (DataType.VARCHAR, DataType.BIT),
        (DataType.VARCHAR, DataType.BIT_VARYING),
        (DataType.VARCHAR, DataType.BOOLEAN),
        # Bit type casts
        (DataType.BIT, DataType.BIT),
        (DataType.BIT, DataType.BIT_VARYING),
        (DataType.BIT, DataType.BOOLEAN),
        (DataType.BIT_VARYING, DataType.BIT_VARYING),
        (DataType.BIT_VARYING, DataType.BIT),
        (DataType.BIT_VARYING, DataType.BOOLEAN),
        # Date/Time type casts
        (DataType.DATE, DataType.DATE),
        (DataType.DATE, DataType.TIMESTAMP),
        (DataType.DATE, DataType.VARCHAR),
        (DataType.DATE, DataType.CHAR),
        (DataType.TIME, DataType.TIME),
        (DataType.TIME, DataType.TIMESTAMP),
        (DataType.TIME, DataType.VARCHAR),
        (DataType.TIME, DataType.CHAR),
        (DataType.TIMESTAMP, DataType.TIMESTAMP),
        (DataType.TIMESTAMP, DataType.DATE),
        (DataType.TIMESTAMP, DataType.TIME),
        (DataType.TIMESTAMP, DataType.VARCHAR),
        (DataType.TIMESTAMP, DataType.CHAR),
        # Boolean type casts
        (DataType.BOOLEAN, DataType.BOOLEAN),
        (DataType.BOOLEAN, DataType.VARCHAR),
        (DataType.BOOLEAN, DataType.CHAR),
        (DataType.BOOLEAN, DataType.BIT),
        (DataType.BOOLEAN, DataType.BIT_VARYING),
    ]
)

INVALID_CASTS = ALL_CAST_PAIRS - set(VALID_CASTS)


class TestDataTypeCasting:
    @pytest.mark.parametrize('source, target', VALID_CASTS)
    def test_can_cast_to_valid(self, source: DataType, target: DataType) -> None:
        assert source.can_cast_to(target)

    @pytest.mark.parametrize('source, target', list(INVALID_CASTS))
    def test_can_cast_to_invalid(self, source: DataType, target: DataType) -> None:
        assert not source.can_cast_to(target)


NULL_COMPARISON_PAIRS = [
    (t, s) for s in ALL_DATATYPES for t in ALL_DATATYPES if s == DataType.NULL or t == DataType.NULL
]


VALID_COMPARABLES = (
    NUMERIC_DATATYPE_PAIRS
    + STRING_DATATYPE_PAIRS
    + NULL_COMPARISON_PAIRS
    + [
        # Bit comparisons
        (DataType.BIT, DataType.BIT),
        (DataType.BIT, DataType.BIT_VARYING),
        (DataType.BIT_VARYING, DataType.BIT),
        (DataType.BIT_VARYING, DataType.BIT_VARYING),
        # Date/Time comparisons
        (DataType.DATE, DataType.DATE),
        (DataType.TIME, DataType.TIME),
        (DataType.TIMESTAMP, DataType.TIMESTAMP),
        # Boolean comparisons
        (DataType.BOOLEAN, DataType.BOOLEAN),
    ]
)

ALL_COMPARABLE_PAIRS = {(lt, rt) for lt in ALL_DATATYPES for rt in ALL_DATATYPES}
INVALID_COMPARABLES = ALL_COMPARABLE_PAIRS - set(VALID_COMPARABLES)


class TestDataTypeComparability:
    @pytest.mark.parametrize('left, right', VALID_COMPARABLES)
    def test_is_comparable_with_valid(self, left: DataType, right: DataType) -> None:
        assert left.is_comparable_with(right)

    @pytest.mark.parametrize('left, right', list(INVALID_COMPARABLES))
    def test_is_comparable_with_invalid(self, left: DataType, right: DataType) -> None:
        assert not left.is_comparable_with(right)
