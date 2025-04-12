from django.urls import reverse

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_name, client_fixture',
    [
        ('common:login', 'unauth_client'),
        ('common:signup', 'unauth_client'),
        ('common:project-list', 'auth_client'),
    ],
)
def test_static_routes_return_200(
    url_name: str, client_fixture: str, request: pytest.FixtureRequest
) -> None:
    client = request.getfixturevalue(client_fixture)
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_detail_returns_200(auth_client: APIClient) -> None:
    mock_id = 1
    url = reverse('common:project-detail', args=[mock_id])
    response = auth_client.get(url)
    assert response.status_code == 200
