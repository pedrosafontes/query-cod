from queries.services.ra.parser.ast import (
    EQ,
    GT,
    GTE,
    LT,
    LTE,
    NEQ,
    And,
    Attribute,
    BinaryBooleanExpression,
    BooleanExpression,
    Comparison,
    ComparisonValue,
    Not,
    Or,
)


def convert_attribute(attr: Attribute) -> str:
    return convert_text(str(attr))


def convert_condition(condition: BooleanExpression) -> str:
    match condition:
        case BinaryBooleanExpression():
            bool_exprs = {
                And: AND_LATEX,
                Or: OR_LATEX,
            }
            return f'({convert_condition(condition.left)} {bool_exprs[type(condition)]} {convert_condition(condition.right)})'
        case Not():
            return f'{NOT_LATEX} ({convert_condition(condition.expression)})'
        case Comparison() as comp:
            comps = {
                EQ: '=',
                NEQ: NEQ_LATEX,
                GT: '>',
                LT: '<',
                GTE: GEQ_LATEX,
                LTE: LEQ_LATEX,
            }
            return f'({_convert_value(comp.left)} {comps[type(comp)]} {_convert_value(comp.right)})'
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


AND_LATEX = '\\land'
OR_LATEX = '\\lor'
NOT_LATEX = '\\lnot'
NEQ_LATEX = '\\neq'
LEQ_LATEX = '\\leq'
GEQ_LATEX = '\\geq'
