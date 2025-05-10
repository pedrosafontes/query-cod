from django.urls import reverse
from django.utils.dateparse import parse_datetime

import pytest
from _pytest.monkeypatch import MonkeyPatch
from model_bakery import baker
from projects.models import Project
from queries.models import Query
from queries.types import QueryError
from queries.views import QueryViewSet
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User


class TestProjectQueries:
    @pytest.mark.django_db
    def test_create_query_for_project(self, auth_client: APIClient, user: User) -> None:
        project = baker.make(Project, user=user)
        url = reverse('project-queries-list', kwargs={'project_pk': project.id})

        payload = {'name': 'My query'}

        response = auth_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED

        query = Query.objects.get(name='My query')
        assert query.project == project
        assert query.sql_text == ''
        assert query.ra_text == ''


class TestQueryCRUD:
    @pytest.mark.django_db
    def test_retrieve_query_returns_query_with_errors(
        self, auth_client: APIClient, user: User, monkeypatch: MonkeyPatch
    ) -> None:
        query = baker.make(Query, project__user=user)
        errors = [QueryError(title='Error')]
        monkeypatch.setattr(
            'queries.models.Query.validation_result',
            (None, errors),
        )

        url = reverse('queries-detail', kwargs={'pk': query.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['id'] == query.id
        assert data['name'] == query.name
        assert data['sql_text'] == query.sql_text
        assert data['ra_text'] == query.ra_text
        assert parse_datetime(data['created']) == query.created
        assert parse_datetime(data['modified']) == query.modified
        assert data['validation_errors'] == errors

    @pytest.mark.django_db
    def test_partial_update_query_returns_query_with_errors(
        self, auth_client: APIClient, user: User, monkeypatch: MonkeyPatch
    ) -> None:
        query = baker.make(Query, project__user=user)
        errors = [QueryError(title='Error')]
        monkeypatch.setattr(
            'queries.models.Query.validation_result',
            (None, errors),
        )

        url = reverse('queries-detail', kwargs={'pk': query.id})
        response = auth_client.patch(url, {'name': 'Updated!'}, content_type='application/json')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['name'] == 'Updated!'
        assert data['validation_errors'] == errors


class TestQueryExecution:
    @pytest.mark.django_db
    def test_execute_query_success(
        self, auth_client: APIClient, user: User, monkeypatch: MonkeyPatch
    ) -> None:
        query = baker.make(Query, project__user=user)

        monkeypatch.setattr(
            'queries.views.execute_query',
            lambda query: {
                'success': True,
                'results': {
                    'columns': ['id'],
                    'rows': [['1']],
                },
            },
        )

        def get_object(self: QueryViewSet) -> Query:
            return query

        monkeypatch.setattr('queries.views.QueryViewSet.get_object', get_object)

        url = reverse('queries-execute', kwargs={'pk': query.id})
        response = auth_client.post(url)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'results' in data

    @pytest.mark.django_db
    def test_execute_query_invalid(
        self, auth_client: APIClient, user: User, monkeypatch: MonkeyPatch
    ) -> None:
        query = baker.make(Query, project__user=user)
        monkeypatch.setattr('queries.models.Query.validation_result', (None, []))

        monkeypatch.setattr('queries.views.QueryViewSet.get_object', lambda self: query)

        url = reverse('queries-execute', kwargs={'pk': query.id})
        response = auth_client.post(url)

        assert response.status_code == 200
        assert response.json() == {'success': False}
