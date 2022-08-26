from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """
    Переопределение пользователя в Django Admin
    """
    model = CustomUser
    list_display = ('username', 'is_admin', 'is_active',)
    list_filter = ('username', 'is_admin', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Permissions'), {
            'fields': ('is_admin',),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_admin',
                       'is_active'),
        }),
    )
    search_fields = ('username',)
    ordering = ('username',)


admin.site.register(CustomUser, CustomUserAdmin)
