from django.db import models
from django.contrib.auth.models import User

class Shop(models.Model):
    """
    Represents ONE shop/business.
    Linked one-to-one with Django User (login account).
    """

    # Auth user (login, password, sessions)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='shop'
    )
    

    # Business details
    shop_name = models.CharField(max_length=150)
    owner_name = models.CharField(max_length=150)

    # Shop lifecycle
    is_active = models.BooleanField(default=True)  
    # False = shop deactivated or deleted

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name
