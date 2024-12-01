from typing import Optional

from users.models import User


class UserRepository:
    @staticmethod
    def create_user(
            email: str,
            name: str,
            password: str,
            is_staff: bool = False
    ) -> User:
        user = User.objects.create_user(
            email=email,
            name=name,
            password=password,
            is_staff=is_staff
        )

        return user

    @staticmethod
    def get_user_by_email(
            email: str
    ) -> Optional[User]:
        return User.objects.filter(email=email).first()
