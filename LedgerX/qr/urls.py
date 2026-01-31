from django.urls import path
from . import views

urlpatterns = [
    path('<str:secure_token>/', views.customer_ledger_qr, name='customer_ledger_qr'),

    path('image/<int:customer_id>/', views.generate_qr_image, name='qr_image'),

    path('<str:secure_token>/transaction/<int:transaction_id>/',
    views.qr_transaction_detail,
    name='qr_transaction_detail'
    ),

<<<<<<< HEAD
=======
    # 🟢 NEW PATH
    path('pay/redirect/', views.payment_bridge_view, name='payment_bridge'),

>>>>>>> 3b92000656ef1a49f15fb9ea26511e4d22fe24a9
]
