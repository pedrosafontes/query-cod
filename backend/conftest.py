import pytest
from model_bakery import baker
from rest_framework.test import APIClient


@pytest.fixture
def user(db):
    user = baker.make("users.User", email="user@email.com")
    user.set_password("123456")
    user.save()
    return user


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.login(email=user.email, password="123456")
    return client


@pytest.fixture
def unauth_client():
    return APIClient()
