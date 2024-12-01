import pytest
from users.models import User


@pytest.mark.django_db
def test_create_superuser_success():
    """
    Test that a superuser is created successfully.
    """
    user_manager = User.objects
    email = "admin@example.com"
    password = "securepassword"
    name = "Admin User"

    superuser = user_manager.create_superuser(
        email=email,
        password=password,
        name=name,
    )

    assert superuser.email == email
    assert superuser.check_password(password)
    assert superuser.is_staff is True
    assert superuser.is_superuser is True
    assert superuser.name == name


@pytest.mark.django_db
def test_create_superuser_missing_name():
    """
    Test that creating a superuser without a name raises a ValueError.
    """
    user_manager = User.objects
    email = "admin@example.com"
    password = "securepassword"

    with pytest.raises(ValueError, match="Superuser must have a name."):
        user_manager.create_superuser(
            email=email,
            password=password,
        )


@pytest.mark.django_db
def test_create_superuser_missing_is_staff():
    """
    Test that creating a superuser with is_staff=False raises a ValueError.
    """
    user_manager = User.objects
    email = "admin@example.com"
    password = "securepassword"
    name = "Admin User"

    with pytest.raises(ValueError, match="Superuser must have is_staff=True."):
        user_manager.create_superuser(
            email=email,
            password=password,
            name=name,
            is_staff=False,
        )


@pytest.mark.django_db
def test_create_superuser_missing_is_superuser():
    """
    Test that creating a superuser with is_superuser=False raises a ValueError.
    """
    user_manager = User.objects
    email = "admin@example.com"
    password = "securepassword"
    name = "Admin User"

    with pytest.raises(ValueError, match="Superuser must have is_superuser=True."):
        user_manager.create_superuser(
            email=email,
            password=password,
            name=name,
            is_superuser=False,
        )
