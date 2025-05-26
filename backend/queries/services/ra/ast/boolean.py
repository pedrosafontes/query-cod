from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .attribute import Attribute
from .base import ASTNode


@dataclass
class BooleanOperation(ASTNode):
    _PRECEDENCE: ClassVar[dict[str, int]] = {
        'Or': 1,
        'And': 2,
        'Not': 3,
    }

    @property
    def precedence(self) -> int:
        return self._PRECEDENCE[type(self).__name__]


@dataclass
class BinaryBooleanExpression(BooleanOperation):
    left: BooleanExpression
    right: BooleanExpression

    @property
    def operator(self) -> str:
        raise NotImplementedError('Subclasses must implement the operator property')

    def __str__(self) -> str:
        return f'({self.left} {self.operator} {self.right})'


@dataclass
class And(BinaryBooleanExpression):
    @property
    def operator(self) -> str:
        return 'and'


class Or(BinaryBooleanExpression):
    @property
    def operator(self) -> str:
        return 'or'


@dataclass
class Not(BooleanOperation):
    expression: BooleanExpression

    def __str__(self) -> str:
        return f'(not {self.expression})'


ComparisonValue = Attribute | str | int | float | bool


@dataclass
class Comparison(ASTNode):
    left: ComparisonValue
    right: ComparisonValue

    @property
    def operator(self) -> str:
        raise NotImplementedError('Subclasses must implement the operator property')

    def __str__(self) -> str:
        return f'{self.left} {self.operator} {self.right}'


@dataclass
class EQ(Comparison):
    @property
    def operator(self) -> str:
        return '='


@dataclass
class NEQ(Comparison):
    @property
    def operator(self) -> str:
        return '<>'


@dataclass
class GT(Comparison):
    @property
    def operator(self) -> str:
        return '>'


@dataclass
class GTE(Comparison):
    @property
    def operator(self) -> str:
        return '>='


@dataclass
class LT(Comparison):
    @property
    def operator(self) -> str:
        return '<'


@dataclass
class LTE(Comparison):
    @property
    def operator(self) -> str:
        return '<='


BooleanExpression = BooleanOperation | Comparison | Attribute
