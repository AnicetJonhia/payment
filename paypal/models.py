from django.db import models
from django.utils import timezone


class Order(models.Model):
    PRODUCT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    product_name = models.CharField(max_length=255)
    amount = models.PositiveIntegerField(help_text="Montant unitaire en cents (ex: 2000 = 20.00 USD)")
    quantity = models.PositiveIntegerField(default=1)
    currency = models.CharField(max_length=3, default='USD')

    # Identifiants externes

    paypal_order_id = models.CharField(max_length=255, blank=True, null=True)

    # Statut de la commande
    status = models.CharField(
        max_length=10,
        choices=PRODUCT_STATUS,
        default='pending',
        help_text="Statut de la commande"
    )

    paid = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order {self.id} - {self.product_name} ({self.status})"
