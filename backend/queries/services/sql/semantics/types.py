from typing import get_args

from sqlglot.expressions import (
    EQ,
    GT,
    GTE,
    LT,
    LTE,
    NEQ,
    Add,
    And,
    Avg,
    Count,
    Div,
    DPipe,
    Except,
    Intersect,
    Length,
    Lower,
    Max,
    Min,
    Mul,
    Not,
    Or,
    StrPosition,
    Sub,
    Substring,
    Sum,
    Trim,
    Union,
    Upper,
)


SetOperation = Union | Intersect | Except
ArithmeticOperation = Add | Sub | Mul | Div
StringOperation = Lower | Upper | Trim | Length | Substring | DPipe | StrPosition
Comparison = EQ | NEQ | GT | GTE | LT | LTE
BooleanExpression = And | Or | Not
AggregateFunction = Count | Sum | Avg | Min | Max
aggregate_functions = get_args(AggregateFunction)
