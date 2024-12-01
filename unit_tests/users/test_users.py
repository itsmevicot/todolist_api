from unittest.mock import MagicMock
import pytest
from users.models import User
from utils.exceptions import UserAlreadyExistsException


@pytest.mark.django_db
def test_create_user(user_repository):
    user = user_repository.create_user(
        email="test@example.com", name="Test User", password="password123"
    )
    assert user.email == "test@example.com"
    assert user.name == "Test User"


@pytest.mark.django_db
def test_get_user_by_email_exists(user_repository):
    created_user = user_repository.create_user(
        email="test@example.com", name="Test User", password="password123"
    )
    user = user_repository.get_user_by_email(email="test@example.com")
    assert user == created_user


@pytest.mark.django_db
def test_get_user_by_email_not_exists(user_repository):
    user = user_repository.get_user_by_email(email="nonexistent@example.com")
    assert user is None


@pytest.mark.django_db
def test_create_user_success(user_service):
    user_mock = User(pk=1, email="test@example.com", name="Test User")
    user_mock.set_password("password123")

    repo_mock = MagicMock()
    repo_mock.get_user_by_email.return_value = None
    repo_mock.create_user.return_value = user_mock

    user_service.user_repository = repo_mock
    data = {"email": "test@example.com", "name": "Test User", "password": "password123"}
    user = user_service.create_user(data)

    assert user.pk == 1
    assert user.email == "test@example.com"


@pytest.mark.django_db
def test_create_user_already_exists(user_service):
    repo_mock = MagicMock()
    repo_mock.get_user_by_email.return_value = MagicMock()

    user_service.user_repository = repo_mock
    data = {"email": "test@example.com", "name": "Test User", "password": "password123"}
    with pytest.raises(UserAlreadyExistsException):
        user_service.create_user(data)


@pytest.mark.django_db
def test_create_user_success_api(api_client):
    data = {"email": "test@example.com", "name": "Test User", "password": "StrongP@ssw0rd!"}
    response = api_client.post("/users/", data)
    assert response.status_code == 201
    assert response.data["email"] == "test@example.com"


@pytest.mark.django_db
def test_create_user_already_exists_api(api_client):
    User.objects.create_user(
        email="test@example.com", name="Test User", password="password123"
    )
    data = {"email": "test@example.com", "name": "Test User", "password": "password123"}
    response = api_client.post("/users/", data)
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_user_validation_error_api(api_client):
    data = {"email": "", "name": "Test User", "password": "password123"}
    response = api_client.post("/users/", data)
    assert response.status_code == 400
    assert "email" in response.data["detail"]
