from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model

from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    PasswordChangeSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """View for user registration."""

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain view that returns user data with tokens."""

    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """View for user logout - blacklists the refresh token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({
                    'error': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                'message': 'Successfully logged out'
            }, status=status.HTTP_200_OK)

        except TokenError:
            return Response({
                'error': 'Invalid or expired token'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating user profile."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    """View for changing user password."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({
                'message': 'Password changed successfully. Please log in again.'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProtectedView(APIView):
    """Example protected endpoint requiring authentication."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'message': 'This is a protected endpoint',
            'user': {
                'id': request.user.id,
                'email': request.user.email,
                'full_name': request.user.get_full_name(),
            }
        }, status=status.HTTP_200_OK)


class AdminOnlyView(APIView):
    """Example endpoint requiring admin privileges."""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response({
            'message': 'This is an admin-only endpoint',
            'user': {
                'id': request.user.id,
                'email': request.user.email,
                'is_staff': request.user.is_staff,
            }
        }, status=status.HTTP_200_OK)
