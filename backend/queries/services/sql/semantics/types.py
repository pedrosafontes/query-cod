from sqlglot.expressions import Add, Div, Lower, Mul, Sub, Trim, Upper


ArithmeticOperation = Add | Sub | Mul | Div
StringOperation = Lower | Upper | Trim
