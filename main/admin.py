from django.contrib import admin

from .models import WinxOrder


@admin.register(WinxOrder)
class WinxOrderAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "method", "discount_claimed", "created_at")
    list_filter = ("method", "discount_claimed", "created_at")
    search_fields = ("full_name", "phone", "address")
    readonly_fields = ("created_at",)
