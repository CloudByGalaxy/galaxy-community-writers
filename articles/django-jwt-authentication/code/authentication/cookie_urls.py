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
