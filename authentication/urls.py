from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    LogoutView,
    UserProfileView,
    UserListView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ChangePasswordView,
    AccountActivateView,
)

urlpatterns = [
    # Inscription / Connexion
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('activate/', AccountActivateView.as_view(), name='auth-activate'),
    path('login/', TokenObtainPairView.as_view(), name='auth-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),

    # Profil
    path('me/', UserProfileView.as_view(), name='auth-profile'),

    # Liste de tous les utilisateurs inscrits
    path('users/', UserListView.as_view(), name='auth-users'),

    # Reset password (par token, sans email)
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password/confirm/', PasswordResetConfirmView.as_view(), name='password-confirm'),

    # Changement de mot de passe (utilisateur connecté)
    path('password/change/', ChangePasswordView.as_view(), name='password-change'),
]
