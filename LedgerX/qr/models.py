from django.db import models
from customers.models import Customer
import uuid

class QRToken(models.Model):
    """
    Secure, public, read-only access to customer ledger.
    """

    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='qr_token'
    )

    # Random, non-guessable token
    secure_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.secure_token)
