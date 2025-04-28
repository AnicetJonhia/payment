from django.db import models

class Order(models.Model):
    product_name = models.CharField(max_length=255)
    amount = models.IntegerField()
    paid = models.BooleanField(default=False)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"Order {self.id} - {self.product_name} x {self.quantity}"
