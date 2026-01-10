from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    LogoutView,
    UserProfileView,
    PasswordChangeView,
    ProtectedView,
    AdminOnlyView,
)

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Token management
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # User profile
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),

    # Protected endpoints examples
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('admin-only/', AdminOnlyView.as_view(), name='admin_only'),
]
