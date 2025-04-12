from datetime import datetime
from typing import TYPE_CHECKING, cast

from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class IndexedTimeStampedModel(models.Model):
    created = cast(datetime, AutoCreatedField(_('created'), db_index=True))  # type: ignore[no-untyped-call]
    modified = cast(datetime, AutoLastModifiedField(_('modified'), db_index=True))  # type: ignore[no-untyped-call]

    class Meta:
        abstract = True

    if TYPE_CHECKING:
        id: int  # noqa: A003
