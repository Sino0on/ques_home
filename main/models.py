from django.db import models


class WinxOrder(models.Model):
    DELIVERY = "delivery"
    PICKUP = "pickup"
    METHOD_CHOICES = [
        (DELIVERY, "Доставка"),
        (PICKUP, "Самовывоз"),
    ]

    full_name = models.CharField("ФИО", max_length=255)
    phone = models.CharField("Телефон", max_length=32)
    method = models.CharField("Способ получения", max_length=16, choices=METHOD_CHOICES)
    address = models.CharField("Адрес доставки", max_length=500, blank=True)
    discount_claimed = models.BooleanField("Скидка 5% (пазл)", default=False)
    created_at = models.DateTimeField("Дата заказа", auto_now_add=True)

    class Meta:
        verbose_name = "Заказ Winx Secret Box"
        verbose_name_plural = "Заказы Winx Secret Box"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.phone} ({self.created_at:%d.%m.%Y %H:%M})"
