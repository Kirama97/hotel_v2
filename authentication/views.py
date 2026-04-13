"""
authentication/views.py

Endpoints :
POST   /api/auth/register/          → Inscription (username + email + password)
POST   /api/auth/login/             → Connexion JWT
POST   /api/auth/token/refresh/     → Rafraîchir le access token
POST   /api/auth/logout/            → Déconnexion (blacklist refresh token)
GET    /api/auth/me/                → Profil utilisateur connecté
PUT    /api/auth/me/                → Modifier le profil
GET    /api/auth/users/             → Liste tous les utilisateurs inscrits
POST   /api/auth/password/reset/    → Demander un token de reset
POST   /api/auth/password/confirm/  → Confirmer le reset
PUT    /api/auth/password/change/   → Changer le mot de passe (connecté)
"""

from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    UserListSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


def get_tokens_for_user(user):
    """Génère les tokens JWT access + refresh pour un utilisateur."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ── Inscription ───────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/

    Corps :
    {
        "username": "john",
        "email": "john@example.com",
        "password": "MonMotDePasse123!"
    }

    Réponse 201 :
    {
        "user": { "id": 1, "username": "john", "email": "john@example.com", ... },
        "tokens": { "access": "...", "refresh": "..." },
        "message": "Compte créé avec succès."
    }
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': get_tokens_for_user(user),
            'message': 'Compte créé avec succès.',
        }, status=status.HTTP_201_CREATED)


# ── Déconnexion ───────────────────────────────────────────────────────────────

class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Corps : { "refresh": "<refresh_token>" }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Le champ "refresh" est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {'message': 'Déconnexion réussie.'},
            status=status.HTTP_205_RESET_CONTENT
        )


# ── Profil ────────────────────────────────────────────────────────────────────

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/auth/me/  → récupérer le profil
    PUT /api/auth/me/  → modifier le profil
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        # Force « partial=True » même pour un PUT
        # Cela empêche l'erreur 400 si le frontend n'envoie pas tous les champs (comme username)
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


# ── Liste des utilisateurs ────────────────────────────────────────────────────

class UserListView(generics.ListAPIView):
    """
    GET /api/auth/users/

    Retourne tous les utilisateurs inscrits avec leur nombre d'hôtels créés.
    Accessible à tout utilisateur connecté.

    Réponse :
    [
        {
            "id": 1,
            "username": "john",
            "email": "john@example.com",
            "date_joined": "2026-03-24T...",
            "total_hotels": 3
        },
        ...
    ]
    """
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.annotate(
            total_hotels=Count('hotels')
        ).order_by('-date_joined')


# ── Reset Password (sans email, par token dans la réponse) ────────────────────

class PasswordResetRequestView(APIView):
    """
    POST /api/auth/password/reset/
    Corps : { "email": "john@example.com" }

    Réponse si l'email existe :
    {
        "message": "Token généré.",
        "token": "550e8400-e29b-41d4-a716-446655440000",
        "expires_in": "24 heures"
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            token = user.generate_reset_token()
            return Response({
                'message': 'Token de réinitialisation généré.',
                'token': str(token),
                'expires_in': '24 heures',
            })
        except User.DoesNotExist:
            # Même réponse pour ne pas révéler si l'email existe
            return Response({
                'message': "Si cet email est associé à un compte, un token a été généré.",
            })


class PasswordResetConfirmView(APIView):
    """
    POST /api/auth/password/confirm/
    Corps :
    {
        "token": "550e8400-...",
        "new_password": "NouveauMdp123!"
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.context['user']
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        user.clear_reset_token()
        return Response({'message': 'Mot de passe réinitialisé avec succès.'})


# ── Changement de mot de passe (utilisateur connecté) ────────────────────────

class ChangePasswordView(APIView):
    """
    PUT /api/auth/password/change/
    Headers : Authorization: Bearer <access_token>
    Corps :
    {
        "old_password": "AncienMdp",
        "new_password": "NouveauMdp123!"
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({
            'message': 'Mot de passe modifié avec succès.',
            'tokens': get_tokens_for_user(request.user),
        })
