from django.urls import reverse
from django.utils.dateparse import parse_datetime

import pytest
from model_bakery import baker
from queries.models import Query
from rest_framework import status


class TestProjectQueries:
    @pytest.mark.django_db
    def test_create_query_for_project(self, auth_client, user):
        project = baker.make('projects.Project', user=user)
        url = reverse('project-queries-list', kwargs={'project_pk': project.id})

        payload = {'name': 'My query', 'text': 'SELECT 1'}

        response = auth_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED

        query = Query.objects.get(name='My query')
        assert query.project == project
        assert query.text == 'SELECT 1'


class TestQueryCRUD:
    @pytest.mark.django_db
    def test_retrieve_query_returns_query_with_errors(self, auth_client, user, monkeypatch):
        query = baker.make(Query, project__user=user)

        def mock_validate():
            return {'valid': True, 'errors': []}

        monkeypatch.setattr(query, 'validate', mock_validate)

        url = reverse('queries-detail', kwargs={'pk': query.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['id'] == query.id
        assert data['name'] == query.name
        assert data['text'] == query.text
        assert parse_datetime(data['created']) == query.created
        assert parse_datetime(data['modified']) == query.modified
        assert data['errors'] == []

    @pytest.mark.django_db
    def test_partial_update_query_returns_query_with_errors(self, auth_client, user, monkeypatch):
        query = baker.make(Query, project__user=user)

        def mock_validate():
            return {'valid': True, 'errors': []}

        monkeypatch.setattr(query, 'validate', mock_validate)

        url = reverse('queries-detail', kwargs={'pk': query.id})
        response = auth_client.patch(url, {'name': 'Updated!'}, content_type='application/json')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['name'] == 'Updated!'
        assert data['errors'] == []


class TestQueryExecution:
    @pytest.mark.django_db
    def test_run_query_success(self, auth_client, user, monkeypatch):
        query = baker.make(Query, project__user=user)

        monkeypatch.setattr(query, 'validate', lambda: {'valid': True})
        monkeypatch.setattr(
            query,
            'execute',
            lambda: {
                'columns': ['id'],
                'rows': [['1']],
            },
        )

        def get_object(self):
            return query

        monkeypatch.setattr('queries.views.QueryViewSet.get_object', get_object)

        url = reverse('queries-run', kwargs={'pk': query.id})
        response = auth_client.post(url)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'results' in data

    @pytest.mark.django_db
    def test_run_query_invalid(self, auth_client, user, monkeypatch):
        query = baker.make(Query, project__user=user)
        monkeypatch.setattr(query, 'validate', lambda: {'valid': False})

        monkeypatch.setattr('queries.views.QueryViewSet.get_object', lambda self: query)

        url = reverse('queries-run', kwargs={'pk': query.id})
        response = auth_client.post(url)

        assert response.status_code == 200
        assert response.json() == {'success': False}
