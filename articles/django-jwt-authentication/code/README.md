# Django JWT Authentication Example

This is a complete, working Django project demonstrating JWT authentication with Django REST Framework.

## Features

- Custom user model with email-based authentication
- User registration with automatic token generation
- JWT token-based authentication (access + refresh tokens)
- HTTP-only cookie authentication option
- Token refresh and rotation
- Token blacklisting for secure logout
- Password change functionality
- Protected endpoints examples
- Comprehensive test suite

## Quick Start

### 1. Set up virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser (optional)

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

## API Endpoints

### Header-based Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register a new user |
| `/api/auth/login/` | POST | Login and get tokens |
| `/api/auth/logout/` | POST | Logout (blacklist refresh token) |
| `/api/auth/token/refresh/` | POST | Refresh access token |
| `/api/auth/token/verify/` | POST | Verify token validity |
| `/api/auth/profile/` | GET/PUT | Get or update user profile |
| `/api/auth/password/change/` | POST | Change password |
| `/api/auth/protected/` | GET | Example protected endpoint |
| `/api/auth/admin-only/` | GET | Example admin-only endpoint |

### Cookie-based Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/cookie/register/` | POST | Register with cookie tokens |
| `/api/auth/cookie/login/` | POST | Login with cookie tokens |
| `/api/auth/cookie/refresh/` | POST | Refresh via cookie |
| `/api/auth/cookie/logout/` | POST | Logout and clear cookies |

## Example API Calls

### Register a new user

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

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Access protected endpoint

```bash
curl -X GET http://localhost:8000/api/auth/protected/ \
  -H "Authorization: Bearer <your_access_token>"
```

### Refresh token

```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<your_refresh_token>"
  }'
```

## Running Tests

```bash
python manage.py test
```

## Project Structure

```
code/
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
│   ├── cookie_urls.py
│   ├── cookie_views.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## License

MIT License
