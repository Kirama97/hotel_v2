from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active', 'date_joined', 'has_reset_token')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'reset_token', 'reset_token_expiry')

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Informations', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
        ('Reset Token', {'fields': ('reset_token', 'reset_token_expiry'), 'classes': ('collapse',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

    def has_reset_token(self, obj):
        return obj.reset_token is not None
    has_reset_token.boolean = True
    has_reset_token.short_description = 'Token actif ?'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
