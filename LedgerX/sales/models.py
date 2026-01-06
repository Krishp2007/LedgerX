from django.db import models
from accounts.models import Shop
from customers.models import Customer

from products.models import Product

class Transaction(models.Model):
    """
    Represents ONE financial action:
    - CASH sale
    - CREDIT sale (bill)
    - PAYMENT (money received)
    """

    CASH = 'CASH'
    CREDIT = 'CREDIT'
    PAYMENT = 'PAYMENT'

    TRANSACTION_TYPES = [
        (CASH, 'Cash Sale'),
        (CREDIT, 'Credit Sale'),
        (PAYMENT, 'Payment'),
    ]

    # Owner shop
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Customer is required ONLY for credit & payment
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )

    # Total bill amount OR payment amount
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Date when transaction happened
    transaction_date = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # Soft delete (rarely used, but safe)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.total_amount}"


class TransactionItem(models.Model):
    """
    Individual product line in a SALE (cash or credit).
    PAYMENT transactions NEVER have items.
    """
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='items'
    )

    # Protect product if used in history
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    # Snapshot price at time of sale
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
