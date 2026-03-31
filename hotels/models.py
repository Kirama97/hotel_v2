"""
hotels/models.py

Modèle Hotel avec :
- Image stockée sur Cloudinary (CloudinaryField)
- Tous les utilisateurs connectés peuvent voir tous les hôtels
- Seul le créateur peut modifier/supprimer son hôtel
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField

User = get_user_model()


class Hotel(models.Model):

    ETOILES_CHOICES = [
        (1, '1 étoile'),
        (2, '2 étoiles'),
        (3, '3 étoiles'),
        (4, '4 étoiles'),
        (5, '5 étoiles'),
    ]

    # ── Informations principales ──────────────────────────────────────────────
    nom            = models.CharField(max_length=200, verbose_name="Nom de l'hôtel")
    description    = models.TextField(blank=True, default='', verbose_name='Description')
    adresse        = models.CharField(max_length=300, verbose_name='Adresse')
    ville          = models.CharField(max_length=100, verbose_name='Ville')
    pays           = models.CharField(max_length=100, default='Sénégal', verbose_name='Pays')
    telephone      = models.CharField(max_length=20, blank=True, default='', verbose_name='Téléphone')
    email_contact  = models.EmailField(blank=True, default='', verbose_name='Email de contact')

    # ── Classement et prix ────────────────────────────────────────────────────
    etoiles = models.IntegerField(
        choices=ETOILES_CHOICES,
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Étoiles"
    )
    prix_par_nuit = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Prix par nuit (XOF)'
    )
    nombre_chambres = models.PositiveIntegerField(default=1, verbose_name='Nombre de chambres')

    # ── Image Cloudinary ──────────────────────────────────────────────────────
    # L'image est automatiquement uploadée sur Cloudinary lors de la sauvegarde
    image = CloudinaryField(
        'image',
        folder='hotels/',     # Dossier dans votre compte Cloudinary
        null=True,
        blank=True,
    )

    # ── Disponibilité ─────────────────────────────────────────────────────────
    est_disponible = models.BooleanField(default=True, verbose_name='Disponible')

    # ── Métadonnées ───────────────────────────────────────────────────────────
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hotels',
        verbose_name='Créé par'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Hôtel'
        verbose_name_plural = 'Hôtels'
        db_table = 'hotels'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nom} ({self.ville}) — {self.etoiles}★"
