from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LogoutView,
    UserProfileView,
    UserListView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ChangePasswordView,
    AccountActivateView,
    CustomTokenObtainPairView,
)

urlpatterns = [

    path('register/', RegisterView.as_view(), name='auth-register'),
    path('activate/', AccountActivateView.as_view(), name='auth-activate'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),

    path('me/', UserProfileView.as_view(), name='auth-profile'),

    path('users/', UserListView.as_view(), name='auth-users'),

    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password/confirm/', PasswordResetConfirmView.as_view(), name='password-confirm'),

    path('password/change/', ChangePasswordView.as_view(), name='password-change'),
]
