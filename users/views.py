from typing import Optional

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import CreateUserSerializer, UserDetailSerializer
from users.service import UserService


class CreateUserView(APIView):
    permission_classes = [AllowAny]

    def __init__(
            self,
            user_service: Optional[UserService] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.user_service = user_service or UserService()

    def post(self, request: Request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.user_service.create_user(serializer.validated_data)
        user_detail_serializer = UserDetailSerializer(user)
        return Response(user_detail_serializer.data, status=status.HTTP_201_CREATED)
