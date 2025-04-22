from collections import defaultdict
from collections.abc import MutableMapping
from typing import Optional

from databases.types import DataType

from .errors import AmbiguousColumnError, UndefinedColumnError


class Scope:
    def __init__(self, parent: Optional['Scope'] = None) -> None:
        self.parent = parent
        # column name (lower case) → list[(table_alias, dtype)]  (list if ambiguous)
        self._symbols: MutableMapping[str, list[tuple[str, DataType]]] = defaultdict(list)

    def add(self, table_alias: str, column: str, dtype: DataType) -> None:
        self._symbols[column.lower()].append((table_alias, dtype))

    def resolve(self, column: str) -> DataType:
        matches = self._symbols.get(column.lower(), [])
        if not matches:
            if self.parent:
                return self.parent.resolve(column)
            else:
                raise UndefinedColumnError(column)

        if len(matches) > 1:
            raise AmbiguousColumnError(column, [tbl for tbl, _ in matches])
        _, dtype = matches[0]
        return dtype
