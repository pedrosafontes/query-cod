from dataclasses import dataclass

from .base import RASyntaxError


@dataclass
class MissingRenameAliasError(RASyntaxError):
    @property
    def title(self) -> str:
        return 'Missing Rename Alias'
