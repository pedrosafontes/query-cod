from enum import Enum


class DataType(Enum):
    SMALLINT = 'smallint'
    INTEGER = 'integer'
    DECIMAL = 'decimal'
    NUMERIC = 'numeric'
    REAL = 'real'
    FLOAT = 'float'
    DOUBLE_PRECISION = 'double_precision'

    CHAR = 'char'
    VARCHAR = 'varchar'

    BIT = 'bit'
    BIT_VARYING = 'bit_varying'

    DATE = 'date'
    TIME = 'time'
    TIMESTAMP = 'timestamp'

    NULL = 'null'

    BOOLEAN = 'boolean'  # SQL:1999+

    def __str__(self) -> str:
        return self.value

    def is_numeric(self) -> bool:
        return self in {
            DataType.SMALLINT,
            DataType.INTEGER,
            DataType.DECIMAL,
            DataType.NUMERIC,
            DataType.REAL,
            DataType.FLOAT,
            DataType.DOUBLE_PRECISION,
        }

    def is_string(self) -> bool:
        return self in {DataType.CHAR, DataType.VARCHAR}

    def is_bit(self) -> bool:
        return self in {DataType.BIT, DataType.BIT_VARYING}

    def is_temporal(self) -> bool:
        return self in {DataType.DATE, DataType.TIME, DataType.TIMESTAMP}

    def is_comparable_with(self, other: 'DataType') -> bool:
        return (
            self == other
            # null is a valid value for all data types
            or self == DataType.NULL
            or other == DataType.NULL
            or (self.is_numeric() and other.is_numeric())
            or (self.is_temporal() and other.is_temporal())
            or (self.is_string() and other.is_string())
            or (self.is_bit() and other.is_bit())
        )

    @classmethod
    def _precedence_list(cls) -> list['DataType']:
        return [
            cls.DOUBLE_PRECISION,
            cls.FLOAT,
            cls.REAL,
            cls.NUMERIC,
            cls.DECIMAL,
            cls.INTEGER,
            cls.SMALLINT,
            cls.VARCHAR,
            cls.CHAR,
            cls.BIT_VARYING,
            cls.BIT,
            cls.TIMESTAMP,
            cls.DATE,
            cls.TIME,
            cls.BOOLEAN,
            cls.NULL,
        ]

    @classmethod
    def _precedence_map(cls) -> dict['DataType', int]:
        return {dt: idx for idx, dt in enumerate(cls._precedence_list())}

    @staticmethod
    def dominant(types: list['DataType']) -> 'DataType':
        if not types:
            raise ValueError()
        return max(types, key=lambda t: DataType._precedence_map().get(t, -1))
