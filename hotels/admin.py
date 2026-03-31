from django.contrib import admin
from .models import Hotel


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'ville', 'pays', 'etoiles',
        'prix_par_nuit', 'est_disponible', 'created_by', 'created_at'
    )
    list_filter  = ('etoiles', 'est_disponible', 'pays', 'ville')
    search_fields = ('nom', 'ville', 'adresse', 'created_by__email')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    ordering = ('-created_at',)
    list_per_page = 25

    fieldsets = (
        ('Informations principales', {
            'fields': ('nom', 'description', 'image')
        }),
        ('Localisation', {
            'fields': ('adresse', 'ville', 'pays')
        }),
        ('Contact', {
            'fields': ('telephone', 'email_contact')
        }),
        ('Tarif & Classement', {
            'fields': ('etoiles', 'prix_par_nuit', 'nombre_chambres', 'est_disponible')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Injecte automatiquement l'utilisateur connecté lors d'une création."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
