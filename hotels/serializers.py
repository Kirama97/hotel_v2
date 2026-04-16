from rest_framework import serializers
from cloudinary.utils import cloudinary_url
from .models import Hotel

class HotelSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    image_url  = serializers.SerializerMethodField()

    class Meta:
        model  = Hotel
        fields = [
            'id', 'nom', 'adresse', 'email_contact', 'telephone',
            'prix_par_nuit', 'devise',
            'image', 'image_url',
            'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at', 'image_url')

    def get_image_url(self, obj):
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
    image_url  = serializers.SerializerMethodField()
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model  = Hotel
        fields = [
            'id', 'nom', 'adresse', 'email_contact', 'telephone',
            'prix_par_nuit', 'devise',
            'image_url', 'created_by', 'created_at',
        ]

    def get_image_url(self, obj):
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
