from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "get_display_name", "is_staff", "created_at")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-created_at",)
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Perfil", {"fields": ("avatar", "bio")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Perfil", {"fields": ("email", "avatar", "bio")}),
    )