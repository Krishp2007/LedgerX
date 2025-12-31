from django.contrib import admin
from .models import Shop

# Register your models here.

class ShopAdmin(admin.ModelAdmin):
    list_display = (
        'shop_name',
        'owner_name',
        'user',
        'is_active',
        'created_at',
    )

    list_filter = ('is_active',)
    search_fields = ('shop_name', 'owner_name', 'user__username', 'user__email')


admin.site.register(Shop, ShopAdmin)
