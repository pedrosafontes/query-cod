class RAValidationError(Exception):
    pass


class UnknownRelationError(RAValidationError):
    def __init__(self, relation: str):
        self.relation = relation
        super().__init__(f'Unknown relation: {relation}')


class UnknownAttributeError(RAValidationError):
    def __init__(self, attribute: str):
        self.attribute = attribute
        super().__init__(f'Unknown attribute: {attribute}')


class AmbiguousAttributeError(RAValidationError):
    def __init__(self, attribute: str, relations: list[str]):
        self.attribute = attribute
        self.relations = relations
        super().__init__(f'Ambiguous attribute: {attribute} in relations: {", ".join(relations)}')
