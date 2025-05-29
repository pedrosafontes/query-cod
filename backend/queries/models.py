from typing import cast

from django.db import models
from django.utils.functional import cached_property

from common.models import IndexedTimeStampedModel
from databases.models import Database

from .services.ra.tree.types import RATree
from .services.sql.tree.types import SQLTree
from .services.tree import QueryTree, Subqueries
from .services.types import QueryAST
from .types import QueryError


class Language(models.TextChoices):
    SQL = 'sql', 'SQL'
    RA = 'ra', 'Relational Algebra'


class AbstractQuery(IndexedTimeStampedModel):
    text = models.TextField(blank=True, default='')

    @property
    def language(self) -> Language:
        raise NotImplementedError()

    @property
    def database(self) -> Database:
        raise NotImplementedError()

    @cached_property
    def validation_result(self) -> tuple[QueryAST | None, list[QueryError]]:
        from .services.validation import validate_query

        return validate_query(self)

    @property
    def is_valid(self) -> bool:
        return self.ast is not None and not self.validation_errors

    @property
    def ast(self) -> QueryAST | None:
        ast, _ = self.validation_result
        return ast

    @property
    def validation_errors(self) -> list[QueryError]:
        _, errors = self.validation_result
        return errors

    @cached_property
    def tree_with_subqueries(self) -> tuple[QueryTree | None, Subqueries]:
        from .services.tree import build_query_tree

        return build_query_tree(self.ast, self.database) if self.ast else (None, {})

    @property
    def _tree(self) -> QueryTree | None:
        tree, _ = self.tree_with_subqueries
        return tree

    @property
    def sql_tree(self) -> SQLTree | None:
        if self._tree and self.language == Language.SQL:
            return cast(SQLTree, self._tree)
        else:
            return None

    @property
    def ra_tree(self) -> RATree | None:
        if self._tree and self.language == Language.RA:
            return cast(RATree, self._tree)
        else:
            return None

    @property
    def subqueries(self) -> Subqueries:
        _, subqueries = self.tree_with_subqueries
        return subqueries

    class Meta:
        abstract = True
