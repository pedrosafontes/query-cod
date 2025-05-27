import copy

from queries.services.types import RelationalSchema


def merge_schemas(
    left: RelationalSchema,
    right: RelationalSchema,
) -> RelationalSchema:
    merged: RelationalSchema = copy.deepcopy(left)
    for rel, attrs in right.items():
        if rel in merged:
            for attr, t in attrs.items():
                merged[rel][attr] = t
        else:
            merged[rel] = dict(attrs)
    return merged
