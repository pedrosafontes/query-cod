from dataclasses import dataclass

from .base import RASyntaxError


@dataclass
class MissingProjectionAttributesError(RASyntaxError):
    @property
    def title(self) -> str:
        return 'Missing Projection Attributes'

    @property
    def description(self) -> str:
        return 'A projection must specify one or more attributes to retain.'
