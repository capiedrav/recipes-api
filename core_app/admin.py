"""
Django admin customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as gt_l
from .models import User, Recipe, Tag


class CustomUserAdmin(UserAdmin):
    """
    Define the admin pages for users.
    """

    ordering = ["id", ]
    list_display = ["email", "name"]

    # define what fields to display in change user page
    fieldsets = (
        (None, {
            "fields": (
                "email",
                "password"
            ),           
        }),
        (gt_l("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser"
            )
        }),
        (gt_l("Important dates"), {
            "fields": ("last_login", )
        }
        )
    )

    readonly_fields = ["last_login", ]

    # define what fields to display in add user page
    add_fieldsets = (
        (None, {
            "classes": ("wide", ),
            "fields": (
                "email",
                "password1",
                "password2",
                "name",
                "is_active",
                "is_staff",
                "is_superuser"
            )
        }),
    )
    


# register models in admin site
admin.site.register(User, CustomUserAdmin)
admin.site.register(Recipe)
admin.site.register(Tag) 
