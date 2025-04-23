from django.db import models

class Order(models.Model):
    product_name = models.CharField(max_length=255)
    amount = models.IntegerField()
    paid = models.BooleanField(default=False)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.product_name} - {'Payée' if self.paid else 'En attente'}"
