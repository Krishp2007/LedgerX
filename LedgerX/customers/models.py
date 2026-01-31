from django.db import models
from accounts.models import Shop

from django.core.validators import RegexValidator

class Customer(models.Model):
    """
    Credit (udhar) customers only.
    Cash customers are NOT stored.
    """

    # Owner shop
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='customers'
    )

    # Customer identity
    name = models.CharField(max_length=150)
    # mobile = models.CharField(max_length=10)
    mobile = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Mobile number must be exactly 10 digits'
            )
        ]
    )

    # Soft delete
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Same mobile can exist in different shops
        unique_together = ('shop', 'mobile')

    def __str__(self):
        return f"{self.name} ({self.mobile})"
