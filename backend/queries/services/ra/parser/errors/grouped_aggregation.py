from dataclasses import dataclass

from .base import RASyntaxError


@dataclass
class GroupedAggregationSyntaxError(RASyntaxError):
    pass


@dataclass
class MissingGroupingAggregationsError(GroupedAggregationSyntaxError):
    def __str__(self) -> str:
        return 'Missing Grouping Aggregations'


@dataclass
class InvalidAggregationInputError(GroupedAggregationSyntaxError):
    def __str__(self) -> str:
        return 'Invalid Aggregation Input'


@dataclass
class InvalidAggregationFunctionError(GroupedAggregationSyntaxError):
    def __str__(self) -> str:
        return 'Invalid Aggregation Function'


@dataclass
class InvalidAggregationOutputError(GroupedAggregationSyntaxError):
    def __str__(self) -> str:
        return 'Invalid Aggregation Output'
