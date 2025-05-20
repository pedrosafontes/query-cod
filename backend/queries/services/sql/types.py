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
    Between,
    Count,
    Div,
    DPipe,
    Exists,
    In,
    Is,
    Length,
    Like,
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
    Upper,
)


ArithmeticOperation = Add | Sub | Mul | Div
StringOperation = Lower | Upper | Trim | Length | Substring | DPipe | StrPosition
Comparison = EQ | NEQ | GT | GTE | LT | LTE
BooleanExpression = And | Or | Not
AggregateFunction = Count | Sum | Avg | Min | Max
aggregate_functions = get_args(AggregateFunction)
Predicate = Exists | Between | Like | Is | In
