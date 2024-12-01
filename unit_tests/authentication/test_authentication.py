import pytest
from rest_framework_simplejwt.tokens import AccessToken


@pytest.mark.django_db
def test_token_obtain(api_client, test_user):
    response = api_client.post(
        "/token/",
        {"email": test_user.email, "password": "password123"}
    )

    assert response.status_code == 200
    assert "access_token" in response.data
    assert "refresh_token" in response.data

    access_token = AccessToken(response.data["access_token"])
    assert access_token["email"] == test_user.email
    assert access_token["name"] == test_user.name


@pytest.mark.django_db
def test_token_refresh(api_client, test_user):
    response = api_client.post(
        "/token/",
        {"email": test_user.email, "password": "password123"}
    )
    assert response.status_code == 200
    refresh_token = response.data["refresh_token"]

    refresh_response = api_client.post(
        "/token/refresh/",
        {"refresh": refresh_token}
    )

    assert refresh_response.status_code == 200
    assert "access" in refresh_response.data

    access_token = AccessToken(refresh_response.data["access"])
    assert access_token["email"] == test_user.email
    assert access_token["name"] == test_user.name
