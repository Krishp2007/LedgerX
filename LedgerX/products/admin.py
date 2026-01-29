from django.contrib import admin
from .models import Product


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'shop',
        'default_price',
        'stock_quantity',
        'is_active',
        'image',
    )

    list_filter = ('shop', 'is_active')
    search_fields = ('name',)


admin.site.register(Product, ProductAdmin)
