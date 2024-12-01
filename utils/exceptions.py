from typing import Optional

from rest_framework import status
from rest_framework.exceptions import APIException


class ExceptionInterface:
    title: Optional[str] = "Something went wrong"
    status_code: Optional[int] = 500
    message: Optional[str] = "An error occurred while processing your request"


class ExceptionMessageBuilder(APIException):
    def __init__(self, ex_info: ExceptionInterface):
        self.title = ex_info.title
        self.status_code = ex_info.status_code
        self.message = ex_info.message


class UserAlreadyExistsException(ExceptionMessageBuilder):
    def __init__(self):
        self.title = "User Already Exists"
        self.message = "A user with this email already exists."
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = {"title": self.title, "message": self.message}
