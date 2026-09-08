from django.contrib import admin

from .models import WinxOrder


@admin.register(WinxOrder)
class WinxOrderAdmin(admin.ModelAdmin):
    list_display = (
        "full_name", "phone", "method", "quantity", "amount",
        "status", "discount_claimed", "created_at",
    )
    list_filter = ("status", "method", "discount_claimed", "created_at")
    search_fields = ("full_name", "phone", "address", "payment_id")
    readonly_fields = ("created_at", "paid_at", "qr_token")
