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
    
    # 📸 NEW FIELD FOR IMAGE
    profile_pic = models.ImageField(upload_to='shop_profiles/', blank=True, null=True)

    # 🟢 NEW FIELD: Store unique UPI ID for this shop
    upi_id = models.CharField(
        max_length=50, 
        default="",       # 🟢 Change this to empty string
        blank=True,       # 🟢 Allows the field to be left empty in forms
        help_text="Your UPI ID (e.g., rahul@oksbi)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name



class PasswordResetOTP(models.Model):
    """
    Stores OTP for password reset.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # Check if OTP is older than 10 minutes
        from django.utils import timezone
        import datetime
        return self.created_at >= timezone.now() - datetime.timedelta(minutes=10)

    def __str__(self):
        return f"OTP for {self.user.email}"

