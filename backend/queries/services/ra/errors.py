class RASyntaxError(Exception):
    def __init__(self, line: int, column: int, label: str = 'Syntax Error', context: str = ''):
        self.label = label
        self.line = line
        self.column = column
        self.context = context

    def __str__(self) -> str:
        return f'{self.label} at line {self.line}, column {self.column}.\n\n{self.context}'


class MismatchedParenthesisError(RASyntaxError):
    label = 'Mismatched Parenthesis'


class MissingCommaError(RASyntaxError):
    label = 'Missing Comma in List'


class MissingOperandError(RASyntaxError):
    label = 'Missing Operand'


class InvalidOperatorError(RASyntaxError):
    label = 'Invalid Operator'


class MissingProjectionAttributesError(RASyntaxError):
    label = 'Missing Projection Attributes'


class MissingSelectionConditionError(RASyntaxError):
    label = 'Missing Selection Condition'


class InvalidSelectionConditionError(RASyntaxError):
    label = 'Invalid Selection Condition'


class MissingThetaJoinConditionError(RASyntaxError):
    label = 'Missing Theta Join Condition'


class InvalidThetaJoinConditionError(RASyntaxError):
    label = 'Invalid Theta Join Condition'


class MissingGroupingAggregationsError(RASyntaxError):
    label = 'Missing Grouping Aggregations'


class InvalidAggregationInputError(RASyntaxError):
    label = 'Invalid Aggregation Input'


class InvalidAggregationFunctionError(RASyntaxError):
    label = 'Invalid Aggregation Function'


class InvalidAggregationOutputError(RASyntaxError):
    label = 'Invalid Aggregation Output'


class InvalidTopNLimitError(RASyntaxError):
    label = 'Invalid Top N Limit'


class InvalidTopNOrderByError(RASyntaxError):
    label = 'Invalid Top N Order By'
