from django.urls import path
from . import views

urlpatterns = [
   path('ledger/<uuid:secure_token>/',views.customer_ledger_qr,name='customer_ledger_qr'),
    path('image/<int:customer_id>/', views.generate_qr_image, name='qr_image'),

    path('<str:secure_token>/transaction/<int:transaction_id>/',
    views.qr_transaction_detail,
    name='qr_transaction_detail'
    ),

]
