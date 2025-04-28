from queries.services.ra.parser.ast import Join, SetOperation, ThetaJoin
from queries.services.ra.semantics.errors import (
    JoinAttributeTypeMismatchError,
)
from queries.services.types import RelationalSchema


def merge_schemas(
    operator: Join | ThetaJoin | SetOperation,
    left: RelationalSchema,
    right: RelationalSchema,
) -> RelationalSchema:
    merged: RelationalSchema = dict(left)
    for rel, attrs in right.items():
        if rel in merged:
            for attr, t in attrs.items():
                if attr in merged[rel] and merged[rel][attr] != t:
                    raise JoinAttributeTypeMismatchError(operator, attr, merged[rel][attr], t)
                merged[rel][attr] = t
        else:
            merged[rel] = dict(attrs)
    return merged
