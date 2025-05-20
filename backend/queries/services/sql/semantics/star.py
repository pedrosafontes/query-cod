from sqlglot.expressions import Expression

from ..scope import SelectScope
from .errors import RelationNotFoundError, UngroupedColumnError


class StarValidator:
    def __init__(self, scope: SelectScope) -> None:
        self.scope = scope

    def validate(self, star: Expression) -> None:
        if not star.is_star:
            raise ValueError('Expected a star expression')

        if not self.scope.is_grouped:
            return

        expanded_cols = self.scope.expand_star(star)
        if expanded_cols is None:
            raise RelationNotFoundError(star)

        # Find columns expanded from star that are not in the GROUP BY
        missing = [col.name for col in expanded_cols if col not in self.scope.group_by]

        if missing:
            raise UngroupedColumnError(star, missing)
