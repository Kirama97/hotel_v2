from django.contrib import admin
from .models import Hotel

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display  = ('nom', 'adresse', 'telephone', 'prix_par_nuit', 'devise', 'created_by', 'created_at')
    search_fields = ('nom', 'adresse', 'email_contact', 'created_by__email')
    readonly_fields = ('created_at', 'updated_at', 'created_by')

    fieldsets = (
        ('Informations', {
            'fields': ('nom', 'adresse', 'email_contact', 'telephone')
        }),
        ('Tarif', {
            'fields': ('prix_par_nuit', 'devise')
        }),
        ('Photo', {
            'fields': ('image',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
