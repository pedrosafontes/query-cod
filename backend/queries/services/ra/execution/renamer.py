from queries.services.ra.parser.ast import (
    Attribute,
    BinaryBooleanExpression,
    BooleanExpression,
    Comparison,
    ComparisonValue,
    NotExpression,
)


class RAExpressionRenamer:
    def __init__(self, renamings: dict[str, str]) -> None:
        self.renamings = renamings

    def rename_attribute(self, attr: Attribute) -> Attribute:
        return Attribute(
            name=attr.name,
            relation=self.renamings.get(attr.relation, attr.relation) if attr.relation else None,
        )

    def _rename_comparison_value(self, value: ComparisonValue) -> ComparisonValue:
        return self.rename_attribute(value) if isinstance(value, Attribute) else value

    def rename_condition(self, cond: BooleanExpression) -> BooleanExpression:
        match cond:
            case BinaryBooleanExpression(operator=operator, left=left, right=right):
                return BinaryBooleanExpression(
                    operator=operator,
                    left=self.rename_condition(left),
                    right=self.rename_condition(right),
                )
            case NotExpression(expression=inner):
                return NotExpression(expression=self.rename_condition(inner))
            case Comparison(left=l, right=r, operator=op):
                return Comparison(
                    left=self._rename_comparison_value(l),
                    right=self._rename_comparison_value(r),
                    operator=op,
                )
            case Attribute() as attr:
                return self.rename_attribute(attr)
            case _:
                raise TypeError(f'Unsupported condition type: {type(cond).__name__}')
