from django.contrib import admin
from .models import QRToken


class QRTokenAdmin(admin.ModelAdmin):
    list_display = (
        'customer',
        'secure_token',
        'is_active',
        'created_at',
    )

    list_filter = ('is_active',)


admin.site.register(QRToken, QRTokenAdmin)
