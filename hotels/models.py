from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField

User = get_user_model()

class Hotel(models.Model):

    DEVISE_CHOICES = [
        ('F XOF', 'F XOF — Franc CFA'),
        ('EUR', 'EUR — Euro'),
        ('USD', 'USD — Dollar américain'),
        ('GBP', 'GBP — Livre sterling'),
    ]

    nom           = models.CharField(max_length=200, verbose_name="Nom de l'hôtel")
    adresse       = models.CharField(max_length=300, verbose_name='Adresse')
    email_contact = models.EmailField(verbose_name='E-mail')
    telephone     = models.CharField(max_length=20, verbose_name='Numéro de téléphone')
    prix_par_nuit = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Prix par nuit'
    )
    devise = models.CharField(
        max_length=10,
        choices=DEVISE_CHOICES,
        default='F XOF',
        verbose_name='Devise'
    )

    image = CloudinaryField(
        'Photo',          
        folder='hotels/',
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='hotels', verbose_name='Créé par'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hôtel'
        verbose_name_plural = 'Hôtels'
        db_table = 'hotels'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nom} — {self.adresse}"
