from django.urls import path
from . import views

urlpatterns = [
    path('<str:secure_token>/', views.customer_ledger_qr, name='customer_ledger_qr'),
]
