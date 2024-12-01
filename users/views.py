from typing import Optional

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from users.serializers import CreateUserSerializer, UserDetailSerializer
from users.service import UserService


class CreateUserView(APIView):
    """
    API view for creating a new user.
    """
    permission_classes = [AllowAny]

    def __init__(
            self,
            user_service: Optional[UserService] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.user_service = user_service or UserService()

    @swagger_auto_schema(
        operation_summary="Create a new user",
        operation_description="Create a new user by providing the required details.",
        request_body=CreateUserSerializer,
        responses={
            201: UserDetailSerializer,
            400: "Invalid data provided.",
        },
    )
    def post(self, request: Request):
        """
        Create a new user.
        """
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.user_service.create_user(serializer.validated_data)
        user_detail_serializer = UserDetailSerializer(user)
        return Response(user_detail_serializer.data, status=status.HTTP_201_CREATED)
