"""
hotels/serializers.py

- HotelSerializer     : version complète (détail, création, modification)
- HotelListSerializer : version allégée (liste)

Les images sont servies depuis Cloudinary avec optimisation automatique
(format auto, qualité auto, redimensionnement).
"""

from rest_framework import serializers
from cloudinary.utils import cloudinary_url
from .models import Hotel


class HotelSerializer(serializers.ModelSerializer):
    """Sérialiseur complet pour create / retrieve / update."""

    created_by      = serializers.StringRelatedField(read_only=True)
    image_url       = serializers.SerializerMethodField()
    etoiles_display = serializers.CharField(source='get_etoiles_display', read_only=True)

    class Meta:
        model  = Hotel
        fields = [
            'id', 'nom', 'description', 'adresse', 'ville', 'pays',
            'telephone', 'email_contact',
            'etoiles', 'etoiles_display',
            'prix_par_nuit', 'nombre_chambres', 'est_disponible',
            'image', 'image_url',
            'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = (
            'id', 'created_by', 'created_at', 'updated_at',
            'image_url', 'etoiles_display'
        )

    def get_image_url(self, obj):
        """
        Retourne l'URL Cloudinary optimisée :
        - Format automatique (webp si le navigateur le supporte)
        - Qualité automatique (compression intelligente)
        - Largeur max 800px
        """
        if obj.image:
            url, _ = cloudinary_url(
                str(obj.image),
                fetch_format='auto',
                quality='auto',
                width=800,
                crop='limit',
            )
            return url
        return None


class HotelListSerializer(serializers.ModelSerializer):
    """Sérialiseur allégé pour la liste des hôtels (GET /api/hotels/)."""

    etoiles_display = serializers.CharField(source='get_etoiles_display', read_only=True)
    image_url       = serializers.SerializerMethodField()
    created_by      = serializers.StringRelatedField(read_only=True)

    class Meta:
        model  = Hotel
        fields = [
            'id', 'nom', 'ville', 'pays',
            'etoiles', 'etoiles_display',
            'prix_par_nuit', 'nombre_chambres',
            'est_disponible', 'image_url',
            'created_by', 'created_at',
        ]

    def get_image_url(self, obj):
        """URL Cloudinary thumbnail pour la liste (400px, recadrage auto)."""
        if obj.image:
            url, _ = cloudinary_url(
                str(obj.image),
                fetch_format='auto',
                quality='auto',
                width=400,
                height=300,
                crop='fill',
                gravity='auto',
            )
            return url
        return None
