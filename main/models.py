import uuid

from django.db import models


class WinxOrder(models.Model):
    DELIVERY = "delivery"
    PICKUP = "pickup"
    METHOD_CHOICES = [
        (DELIVERY, "Доставка"),
        (PICKUP, "Самовывоз"),
    ]

    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Ожидает оплаты"),
        (STATUS_PAID, "Оплачен"),
        (STATUS_FAILED, "Не оплачен / отменён"),
    ]

    full_name = models.CharField("ФИО", max_length=255)
    phone = models.CharField("Телефон", max_length=32)
    method = models.CharField("Способ получения", max_length=16, choices=METHOD_CHOICES)
    address = models.CharField("Адрес доставки", max_length=500, blank=True)
    discount_claimed = models.BooleanField("Скидка 5% (пазл)", default=False)

    quantity = models.PositiveIntegerField("Количество боксов", default=1)
    amount = models.DecimalField("Сумма, сом", max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        "Статус оплаты", max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    qr_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    payment_id = models.CharField("ID платежа Finik", max_length=100, blank=True)
    paid_at = models.DateTimeField("Оплачен", blank=True, null=True)

    created_at = models.DateTimeField("Дата заказа", auto_now_add=True)

    class Meta:
        verbose_name = "Заказ Winx Secret Box"
        verbose_name_plural = "Заказы Winx Secret Box"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.phone} ({self.created_at:%d.%m.%Y %H:%M})"

    @property
    def is_paid(self):
        return self.status == self.STATUS_PAID
