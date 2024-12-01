from django.shortcuts import redirect
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from authentication.views import CustomTokenObtainPairView

urlpatterns = [
    path('', lambda request: redirect('schema-swagger-ui', permanent=True)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
