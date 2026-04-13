"""
authentication/models.py

Modèle User personnalisé :
- Connexion par email (pas par username)
- Champs reset_token + reset_token_expiry pour reset password sans email
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Utilisateur personnalisé.
    L'email est l'identifiant de connexion (USERNAME_FIELD = 'email').
    """

    email = models.EmailField(unique=True, verbose_name='Adresse email')
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True, verbose_name='Photo de profil')

    # Champs pour le reset password par token (sans envoi email)
    reset_token = models.UUIDField(null=True, blank=True, default=None)
    reset_token_expiry = models.DateTimeField(null=True, blank=True, default=None)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        db_table = 'auth_users'

    def __str__(self):
        return self.email

    # ── Méthodes reset password ───────────────────────────────────────────────

    def generate_reset_token(self):
        """Génère un token UUID valable 24h. Retourne le token."""
        from django.conf import settings
        hours = getattr(settings, 'PASSWORD_RESET_TOKEN_EXPIRY_HOURS', 24)
        self.reset_token = uuid.uuid4()
        self.reset_token_expiry = timezone.now() + timezone.timedelta(hours=hours)
        self.save(update_fields=['reset_token', 'reset_token_expiry'])
        return self.reset_token

    def is_reset_token_valid(self):
        """Vérifie que le token existe et n'est pas expiré."""
        if not self.reset_token or not self.reset_token_expiry:
            return False
        return timezone.now() <= self.reset_token_expiry

    def clear_reset_token(self):
        """Invalide le token après utilisation (usage unique)."""
        self.reset_token = None
        self.reset_token_expiry = None
        self.save(update_fields=['reset_token', 'reset_token_expiry'])
