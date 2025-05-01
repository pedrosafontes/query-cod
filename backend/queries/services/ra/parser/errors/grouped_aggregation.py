from dataclasses import dataclass

from .base import RASyntaxError


@dataclass
class GroupedAggregationSyntaxError(RASyntaxError):
    pass


@dataclass
class MissingGroupingAggregationsError(GroupedAggregationSyntaxError):
    @property
    def title(self) -> str:
        return 'Missing Grouping Aggregations'

    @property
    def description(self) -> str:
        return 'Group-by queries must include at least one aggregation function.'


@dataclass
class InvalidAggregationInputError(GroupedAggregationSyntaxError):
    @property
    def title(self) -> str:
        return 'Invalid Aggregation Input'

    @property
    def description(self) -> str:
        return 'The input to aggregation functions must be a valid attribute.'


@dataclass
class InvalidAggregationFunctionError(GroupedAggregationSyntaxError):
    @property
    def title(self) -> str:
        return 'Invalid Aggregation Function'

    @property
    def description(self) -> str:
        return 'The specified aggregation function is not supported. It must be one of: count, sum, avg, min, max.'


@dataclass
class InvalidAggregationOutputError(GroupedAggregationSyntaxError):
    @property
    def title(self) -> str:
        return 'Invalid Aggregation Output'

    @property
    def description(self) -> str:
        return 'The output to aggregation functions must be a valid attribute.'
