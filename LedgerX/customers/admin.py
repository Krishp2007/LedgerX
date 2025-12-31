from django.contrib import admin
from .models import Customer


class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'mobile',
        'shop',
        'is_active',
        'created_at',
    )

    list_filter = ('shop', 'is_active')
    search_fields = ('name', 'mobile')


admin.site.register(Customer, CustomerAdmin)
