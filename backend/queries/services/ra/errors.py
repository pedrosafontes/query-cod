class RASyntaxError(SyntaxError):
    def __str__(self):
        context, line, column = self.args
        return f'{self.label} at line {line}, column {column}.\n\n{context}'


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
