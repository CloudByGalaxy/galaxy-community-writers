# How to Implement JWT Authentication in Django REST Framework

**Author:** Isijola Jeremiah (@userJeremiah)
**Theme:** Django Development / Security & Authentication
**Target Audience:** Intermediate to Advanced
**Word Count:** 4500+

---

## Introduction

When building a backend with Django, authentication is one of the first critical decisions you make. Among the many available approaches, combining Django REST Framework (DRF) with JSON Web Tokens (JWT) has become my preferred solution. JWTs keep authentication stateless, flexible, and straightforward to integrate with modern frontends—whether you're building a React SPA, a mobile app, or consuming your API from any client.

In this comprehensive guide, I will walk you through how I personally handle JWT authentication in Django projects. We'll cover everything from initial setup and configuration to issuing tokens, protecting API routes, implementing token refresh, and working with HTTP-only cookies for enhanced security. By the end, you'll have a production-ready authentication system that is both secure and developer-friendly.

## Prerequisites

Before diving in, make sure you have:

- Python 3.8 or higher installed
- Basic familiarity with Django and Django REST Framework
- Understanding of HTTP requests and RESTful APIs
- A code editor and terminal access

## Why JWT Authentication?

Before we start coding, let's understand why JWT is an excellent choice for API authentication:

### Stateless Architecture

Unlike session-based authentication that requires server-side storage, JWTs are self-contained. The token itself carries all the necessary user information and claims, allowing your server to validate requests without database lookups for session data.

### Scalability

Because JWTs are stateless, they work seamlessly across multiple server instances. You don't need sticky sessions or shared session storage—any server with the secret key can validate the token.

### Cross-Platform Compatibility

JWTs work identically across web browsers, mobile applications, and server-to-server communication. This makes them ideal for applications with multiple client types.

### Flexible Claims

JWTs can carry custom claims (user roles, permissions, metadata), reducing the need for additional database queries when authorizing requests.

## Project Setup

Let's start by creating a new Django project with all the necessary dependencies.

### Step 1: Create Virtual Environment and Install Dependencies

```bash
# Create a new directory for your project
mkdir django_jwt_auth
cd django_jwt_auth

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install django djangorestframework djangorestframework-simplejwt python-dotenv
```

We're using `djangorestframework-simplejwt`, which is the most widely adopted and actively maintained JWT library for Django REST Framework. It provides a robust implementation with sensible defaults and extensive customization options.

### Step 2: Create Django Project and App

```bash
# Create Django project
django-admin startproject core .

# Create authentication app
python manage.py startapp authentication
```

### Step 3: Project Structure

Your project should now look like this:

```
django_jwt_auth/
├── core/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── authentication/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   └── tests.py
├── manage.py
└── venv/
```

## Configuration

### Step 4: Configure Django Settings

Update your `core/settings.py` with the necessary configurations:

```python
# core/settings.py
from datetime import timedelta
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # For token blacklisting
    # Local apps
    'authentication',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Simple JWT Configuration
SIMPLE_JWT = {
    # Token Lifetimes
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),

    # Token Rotation
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    # Algorithm and Signing Key
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,

    # Token Types
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',

    # User ID Configuration
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    # Token Classes
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    # JTI Claim for token identification
    'JTI_CLAIM': 'jti',
}
```

Let's break down the key JWT settings:

- **ACCESS_TOKEN_LIFETIME**: Short-lived tokens (15 minutes) that clients use for API requests
- **REFRESH_TOKEN_LIFETIME**: Long-lived tokens (7 days) used to obtain new access tokens
- **ROTATE_REFRESH_TOKENS**: Issues a new refresh token with each refresh request
- **BLACKLIST_AFTER_ROTATION**: Invalidates old refresh tokens after rotation for security

## Creating the User Model

### Step 5: Custom User Model

While Django's default User model works, creating a custom user model gives you flexibility for future requirements:

```python
# authentication/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Custom manager for CustomUser model."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom user model that uses email instead of username."""

    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.email

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]
```

Add this to your settings:

```python
# core/settings.py
AUTH_USER_MODEL = 'authentication.CustomUser'
```

## Creating Serializers

### Step 6: User and Token Serializers

```python
# authentication/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name',
                  'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'is_active']

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Password fields do not match.'
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that includes user data in response."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims to the token
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['full_name'] = user.get_full_name()

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user data to the response
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'full_name': self.user.get_full_name(),
        }

        return data


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""

    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'New password fields do not match.'
            })
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value
```

## Creating Views

### Step 7: Authentication Views

```python
# authentication/views.py
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
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

        except TokenError as e:
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

            # Blacklist all existing refresh tokens for security
            # User will need to log in again
            return Response({
                'message': 'Password changed successfully. Please log in again.'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

## Setting Up URLs

### Step 8: Configure URL Routing

```python
# authentication/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    LogoutView,
    UserProfileView,
    PasswordChangeView,
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
]
```

```python
# core/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
]
```

## HTTP-Only Cookie Authentication

For enhanced security, especially when working with web frontends, you can use HTTP-only cookies to store tokens. This prevents JavaScript from accessing the tokens, protecting against XSS attacks.

### Step 9: Cookie-Based Token Views

```python
# authentication/cookie_views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
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

        except TokenError as e:
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
```

Add the cookie-based URLs:

```python
# authentication/cookie_urls.py
from django.urls import path

from .cookie_views import (
    CookieRegisterView,
    CookieLoginView,
    CookieRefreshView,
    CookieLogoutView,
)

urlpatterns = [
    path('register/', CookieRegisterView.as_view(), name='cookie_register'),
    path('login/', CookieLoginView.as_view(), name='cookie_login'),
    path('refresh/', CookieRefreshView.as_view(), name='cookie_refresh'),
    path('logout/', CookieLogoutView.as_view(), name='cookie_logout'),
]
```

Update the main urls:

```python
# core/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/auth/cookie/', include('authentication.cookie_urls')),
]
```

## Protecting API Routes

### Step 10: Creating Protected Endpoints

Let's create an example protected resource:

```python
# authentication/protected_views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser


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
```

## Testing the API

### Step 11: Run Migrations and Create Test Data

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser for testing
python manage.py createsuperuser
```

### Step 12: Testing with cURL

Here are examples of how to test each endpoint:

**Register a new user:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Access protected endpoint:**
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer <your_access_token>"
```

**Refresh token:**
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<your_refresh_token>"
  }'
```

## Security Best Practices

When implementing JWT authentication in production, consider these security measures:

### 1. Use Strong Secret Keys

```python
# Generate a strong secret key
import secrets
print(secrets.token_urlsafe(64))
```

### 2. Configure HTTPS

Always use HTTPS in production to prevent token interception:

```python
# core/settings.py (production)
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 3. Implement Rate Limiting

```bash
pip install django-ratelimit
```

```python
# authentication/views.py
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST'))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
```

### 4. Token Lifetime Considerations

- Access tokens: Keep short (5-15 minutes)
- Refresh tokens: Reasonable duration (1-7 days)
- Rotate refresh tokens on each use
- Implement token blacklisting for logout

## Deploying to Galaxy

When you're ready to deploy your Django application with JWT authentication, Galaxy Cloud provides an excellent platform with minimal configuration. Here's how to prepare your application:

### Environment Configuration

Create a `.env` file for production:

```bash
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.galaxycloud.app
DATABASE_URL=your-database-url
```

### Requirements File

```txt
# requirements.txt
Django>=4.2
djangorestframework>=3.14
djangorestframework-simplejwt>=5.3
python-dotenv>=1.0
gunicorn>=21.0
psycopg2-binary>=2.9  # For PostgreSQL
```

Galaxy simplifies deployment with automatic SSL certificates, scaling, and monitoring capabilities that work seamlessly with Django applications.

## Conclusion

In this guide, we've built a comprehensive JWT authentication system for Django REST Framework that includes:

- Custom user model with email-based authentication
- User registration with automatic token generation
- Login with custom claims in JWT tokens
- Token refresh and rotation for security
- Token blacklisting for secure logout
- HTTP-only cookie authentication option
- Protected endpoints with permission classes
- Password change functionality

This implementation provides a solid foundation for any Django API requiring authentication. The stateless nature of JWTs makes it easy to scale your application horizontally, while the token blacklisting feature ensures you can invalidate sessions when needed.

From here, you can extend this foundation with additional features like:
- Email verification for new accounts
- Password reset functionality
- Role-based access control (RBAC)
- OAuth2/social authentication integration
- Multi-factor authentication (MFA)

The flexibility of Django REST Framework combined with SimpleJWT gives you all the tools needed to build secure, production-ready APIs.
