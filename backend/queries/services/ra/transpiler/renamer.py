from queries.services.ra.parser.ast import (
    Attribute,
    BinaryBooleanExpression,
    BooleanExpression,
    Comparison,
    ComparisonValue,
    Not,
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
            case BinaryBooleanExpression(left=left, right=right):
                return type(cond)(
                    left=self.rename_condition(left),
                    right=self.rename_condition(right),
                )
            case Not(expression=inner):
                return Not(expression=self.rename_condition(inner))
            case Comparison(left=left, right=right):
                return type(cond)(
                    left=self._rename_comparison_value(left),
                    right=self._rename_comparison_value(right),
                )
            case Attribute() as attr:
                return self.rename_attribute(attr)
            case _:
                raise TypeError(f'Unsupported condition type: {type(cond).__name__}')
