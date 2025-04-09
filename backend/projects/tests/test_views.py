from django.urls import reverse

import pytest
from model_bakery import baker
from projects.models import Project
from rest_framework import status


@pytest.mark.django_db
def test_list_projects_returns_only_user_projects(auth_client, user):
    user_project = baker.make(Project, user=user)

    # Project belonging to someone else
    other_user = baker.make('users.User')
    baker.make(Project, user=other_user, _quantity=3)

    url = reverse('projects-list')
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) == 1
    assert data[0]['id'] == user_project.id


@pytest.mark.django_db
def test_create_project_sets_user(auth_client, user):
    url = reverse('projects-list')

    payload = {'name': 'My new project', 'database_id': baker.make('databases.Database').id}

    response = auth_client.post(url, data=payload)

    assert response.status_code == status.HTTP_201_CREATED
    project = Project.objects.get(name='My new project')

    assert project.user == user
    assert project.database.id == payload['database_id']
