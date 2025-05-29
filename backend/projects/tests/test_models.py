from datetime import timedelta

from django.utils import timezone

import pytest
from model_bakery import baker
from projects.models import Project


@pytest.mark.django_db
def test_with_last_modified_returns_ordered_projects() -> None:
    # Create two projects with different query timestamps
    project1 = baker.make(Project)
    project2 = baker.make(Project)

    baker.make(
        'projects.Query',
        project=project1,
        created=timezone.now() - timedelta(days=2),
        modified=timezone.now() - timedelta(days=2),
    )

    baker.make(
        'projects.Query',
        project=project2,
        created=timezone.now(),
        modified=timezone.now(),
    )

    projects = Project.with_last_modified()

    assert len(projects) == 2
    assert projects[0].id == project2.id  # most recently modified project comes first
    assert hasattr(projects[0], 'last_modified')
    assert projects[0].last_modified >= projects[1].last_modified
