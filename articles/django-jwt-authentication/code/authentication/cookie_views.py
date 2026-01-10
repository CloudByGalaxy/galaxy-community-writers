from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from django.contrib.auth import get_user_model

from .serializers import UserSerializer, UserRegistrationSerializer

User = get_user_model()


class CookieJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication that reads tokens from cookies."""

    def authenticate(self, request):
        # First try to get the token from the cookie
        raw_token = request.COOKIES.get('access_token')

        if raw_token is None:
            # Fall back to header-based authentication
            return super().authenticate(request)

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token


def get_tokens_for_user(user):
    """Generate access and refresh tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def set_token_cookies(response, tokens):
    """Set JWT tokens as HTTP-only cookies."""
    # Access token cookie settings
    response.set_cookie(
        key='access_token',
        value=tokens['access'],
        max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
        secure=not settings.DEBUG,  # Use secure cookies in production
        httponly=True,
        samesite='Lax',
        path='/',
    )

    # Refresh token cookie settings
    response.set_cookie(
        key='refresh_token',
        value=tokens['refresh'],
        max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        secure=not settings.DEBUG,
        httponly=True,
        samesite='Lax',
        path='/api/auth/',  # Restrict refresh token to auth endpoints
    )

    return response


def clear_token_cookies(response):
    """Clear JWT token cookies."""
    response.delete_cookie('access_token', path='/')
    response.delete_cookie('refresh_token', path='/api/auth/')
    return response


class CookieRegisterView(APIView):
    """User registration with cookie-based tokens."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)

            response = Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
            }, status=status.HTTP_201_CREATED)

            return set_token_cookies(response, tokens)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CookieLoginView(APIView):
    """User login with cookie-based tokens."""

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({
                'error': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'error': 'User account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)

        tokens = get_tokens_for_user(user)

        response = Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)

        return set_token_cookies(response, tokens)


class CookieRefreshView(APIView):
    """Refresh access token using cookie-based refresh token."""

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({
                'error': 'Refresh token not found'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            tokens = {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }

            # Rotate refresh token if configured
            if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
                refresh.blacklist()
                new_refresh = RefreshToken.for_user(
                    User.objects.get(id=refresh['user_id'])
                )
                tokens['refresh'] = str(new_refresh)
                tokens['access'] = str(new_refresh.access_token)

            response = Response({
                'message': 'Token refreshed successfully'
            }, status=status.HTTP_200_OK)

            return set_token_cookies(response, tokens)

        except TokenError:
            response = Response({
                'error': 'Invalid or expired refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)
            return clear_token_cookies(response)


class CookieLogoutView(APIView):
    """User logout with cookie-based tokens."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass  # Token already invalid

        response = Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)

        return clear_token_cookies(response)
