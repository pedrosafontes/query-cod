import re

import sqlglot.expressions as exp
from databases.types import DataType


def infer_literal_type(node: exp.Literal) -> DataType:
    value = node.this

    if node.is_int:
        return DataType.INTEGER
    elif node.is_number:
        return DataType.FLOAT
    elif node.is_string:
        value = str(value).lower()
        if value in {'true', 'false'}:
            return DataType.BOOLEAN
        elif value in {'null', 'none'}:
            return DataType.NULL
        elif is_date_format(value):
            return DataType.DATE
        elif is_time_format(value):
            return DataType.TIME
        elif is_timestamp_format(value):
            return DataType.TIMESTAMP
        else:
            return DataType.VARCHAR
    else:
        raise ValueError(f'Unsupported literal: {node}')


def is_date_format(s: str) -> bool:
    return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', s))


def is_time_format(s: str) -> bool:
    return bool(re.fullmatch(r'\d{2}:\d{2}(:\d{2})?', s))


def is_timestamp_format(s: str) -> bool:
    return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?', s))
