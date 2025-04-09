from django.urls import reverse

import pytest
from rest_framework import status
from users.models import User


@pytest.fixture
def user(db):
    user = User.objects.create_user(
        email="user@example.com",
        password="testpass123",
    )
    return user


@pytest.mark.django_db
def test_login_success(client, user):
    url = reverse("login")

    response = client.post(url, {
        "username": user.email,
        "password": "testpass123",
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Successfully logged in."


@pytest.mark.django_db
def test_login_failure_wrong_password(client, user):
    url = reverse("login")

    response = client.post(url, {
        "username": user.email,
        "password": "wrongpass",
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_login_failure_unknown_user(client):
    url = reverse("login")

    response = client.post(url, {
        "username": "unknown@example.com",
        "password": "whatever",
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_logout_clears_session(client, user):
    login_url = reverse("login")
    logout_url = reverse("logout")
    protected_url = reverse("projects-list")

    # Login
    login_response = client.post(login_url, {
        "username": user.email,
        "password": "testpass123",
    })
    assert login_response.status_code == 200

    # Access a protected view
    auth_response = client.get(protected_url)
    assert auth_response.status_code == 200

    # Logout
    logout_response = client.post(logout_url)
    assert logout_response.status_code == 200
    assert logout_response.json()["detail"] == "Successfully logged out."

    # Access protected view again — should fail with 403 or 401
    post_logout_response = client.get(protected_url)
    assert post_logout_response.status_code in [401, 403]
