from dataclasses import dataclass

from .base import RASyntaxError


@dataclass
class MissingProjectionAttributesError(RASyntaxError):
    def __str__(self) -> str:
        return 'Missing Projection Attributes'
