from queries.services.ra.parser.ast import (
    Attribute,
    BinaryBooleanExpression,
    BinaryBooleanOperator,
    BooleanExpression,
    Comparison,
    ComparisonOperator,
    ComparisonValue,
    NotExpression,
)


def convert_attribute(attr: Attribute) -> str:
    return convert_text(str(attr))


def convert_condition(condition: BooleanExpression) -> str:
    match condition:
        case BinaryBooleanExpression(operator=op):
            match op:
                case BinaryBooleanOperator.AND:
                    operator_label = LAND
                case BinaryBooleanOperator.OR:
                    operator_label = LOR
            return f'({convert_condition(condition.left)} {operator_label} {convert_condition(condition.right)})'
        case NotExpression():
            return f'{LNOT} ({convert_condition(condition.expression)})'
        case Comparison(operator=op):
            match op:
                case ComparisonOperator.EQUAL:
                    operator_label = '='
                case ComparisonOperator.NOT_EQUAL:
                    operator_label = NEQ
                case ComparisonOperator.GREATER_THAN:
                    operator_label = '>'
                case ComparisonOperator.GREATER_THAN_EQUAL:
                    operator_label = GEQ
                case ComparisonOperator.LESS_THAN:
                    operator_label = '<'
                case ComparisonOperator.LESS_THAN_EQUAL:
                    operator_label = LEQ
            return f'({_convert_value(condition.left)} {operator_label} {_convert_value(condition.right)})'
        case Attribute() as attr:
            return convert_attribute(attr)
        case _:
            return str(condition)


def _convert_value(value: ComparisonValue) -> str:
    match value:
        case Attribute() as attr:
            return convert_attribute(attr)
        case str() as string_value:
            return convert_text(f"'{string_value}'")
        case int() | float() | bool() as number_value:
            return str(number_value)


def convert_text(text: str) -> str:
    replacements = {
        '\\': r'\\textbackslash{}',
        '{': r'\{',
        '}': r'\}',
        '_': r'\_',
        '^': r'\^{}',
        '#': r'\#',
        '$': r'\$',
        '%': r'\%',
        '&': r'\&',
        '~': r'\\textasciitilde{}',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return f'\\text{{{text}}}'


LAND = '\\land'
LOR = '\\lor'
LNOT = '\\lnot'
NEQ = '\\neq'
LEQ = '\\leq'
GEQ = '\\geq'
