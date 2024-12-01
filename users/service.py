from typing import Optional

from rest_framework.exceptions import ValidationError

from users.repository import UserRepository


class UserService:
    def __init__(
            self,
            user_repository: Optional[UserRepository] = None,
    ):
        self.user_repository = user_repository or UserRepository()

    def create_user(
            self,
            email: str,
            name: str,
            password: str
    ):
        if not email or not name or not password:
            raise ValidationError("E-mail, name, and password are required.")

        user = self.user_repository.create_user(email=email, name=name, password=password)
        return user
