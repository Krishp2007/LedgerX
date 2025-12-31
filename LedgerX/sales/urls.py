from django.urls import path
from . import views

urlpatterns = [
    # Sales
    path('add/', views.add_sale, name='add_sale'),

    # Payments
    path('payment/add/', views.add_payment, name='add_payment'),
    path('payment/add/<int:customer_id>/', views.add_payment_for_customer, name='add_payment_for_customer'),

    # Read-only transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
]
