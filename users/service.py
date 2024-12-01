import logging
from typing import Optional, Dict

from django.db import transaction

from users.models import User
from users.repository import UserRepository
from utils.exceptions import UserAlreadyExistsException
from users.tasks import send_welcome_email

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
            self,
            user_repository: Optional[UserRepository] = None,
    ):
        self.user_repository = user_repository or UserRepository()

    @transaction.atomic
    def create_user(self, data: Dict) -> User:
        try:
            if self.user_repository.get_user_by_email(data.get("email")):
                raise UserAlreadyExistsException()
            logger.info(f"Creating user with data: {data}")
            user = self.user_repository.create_user(**data)
            logger.info(f"Created user with ID: {user.pk}")
            send_welcome_email.delay(user.email, user.name)
            logger.info(f"Welcome email task triggered for user ID: {user.id}")
            return user

        except UserAlreadyExistsException as e:
            logger.error(f"User already exists: {e.detail}")
            raise

        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise
