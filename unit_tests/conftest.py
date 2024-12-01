import pytest
from rest_framework.test import APIClient

from users.models import User
from users.repository import UserRepository
from users.service import UserService


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_repository():
    return UserRepository()


@pytest.fixture
def user_service(user_repository):
    return UserService(user_repository=user_repository)


@pytest.fixture
def test_user(db):
    """
    Create and return a test user.
    """
    user = User.objects.create_user(
        name="Test",
        email="testuser@example.com",
        password="password123",
    )
    return user
