from sqlglot.expressions import Add, Div, Except, Intersect, Lower, Mul, Sub, Trim, Union, Upper


SetOperation = Union | Intersect | Except
ArithmeticOperation = Add | Sub | Mul | Div
StringOperation = Lower | Upper | Trim
