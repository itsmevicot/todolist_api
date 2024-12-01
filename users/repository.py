from authentication.models import User


class UserRepository:
    @staticmethod
    def create_user(
            email: str,
            name: str,
            password: str,
            is_staff: bool = False
    ):
        user = User.objects.create_user(
            email=email,
            name=name,
            password=password,
            is_staff=is_staff
        )

        return user
