"""
authentication/serializers.py

Sérialiseurs pour :
- Inscription (username + email + password UNIQUEMENT, pas de confirm)
- Profil utilisateur
- Liste des utilisateurs inscrits
- Reset password par token
- Changement de mot de passe
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


# ── Inscription ───────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    """
    Inscription simplifiée : username + email + password uniquement.
    Pas de champ password2 / confirm password.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        read_only_fields = ('id',)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un compte avec cet email existe déjà.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )


# ── Profil ────────────────────────────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile_picture', 'date_joined')
        read_only_fields = ('id', 'email', 'date_joined')


# ── Liste utilisateurs ────────────────────────────────────────────────────────

class UserListSerializer(serializers.ModelSerializer):
    """
    Liste de tous les utilisateurs inscrits.
    Inclut le nombre d'hôtels créés par chaque utilisateur.
    """
    total_hotels = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_picture', 'date_joined', 'total_hotels')


# ── Reset Password ────────────────────────────────────────────────────────────

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField(required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    def validate_token(self, value):
        try:
            user = User.objects.get(reset_token=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Token invalide ou déjà utilisé.")
        if not user.is_reset_token_valid():
            raise serializers.ValidationError("Ce token a expiré. Refaites une demande.")
        self.context['user'] = user
        return value


# ── Changement de mot de passe (utilisateur connecté) ────────────────────────

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True, required=True,
        validators=[validate_password], style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError("L'ancien mot de passe est incorrect.")
        return value
