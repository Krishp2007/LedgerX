from django.contrib import admin
from .models import Transaction, TransactionItem


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price_at_sale')


class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'shop',
        'transaction_type',
        'customer',
        'total_amount',
        'transaction_date',
    )

    list_filter = ('transaction_type', 'shop')
    search_fields = ('id',)
    inlines = [TransactionItemInline]


admin.site.register(Transaction, TransactionAdmin)


class TransactionItemAdmin(admin.ModelAdmin):
    list_display = (
        'transaction',
        'product',
        'quantity',
        'price_at_sale',
    )


admin.site.register(TransactionItem, TransactionItemAdmin)
