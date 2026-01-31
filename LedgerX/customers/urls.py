from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    path('add/', views.customer_add, name='customer_add'),
    path('<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('<int:customer_id>/edit/', views.customer_edit, name='customer_edit'),
    path('<int:customer_id>/deactivate/', views.customer_deactivate, name='customer_deactivate'),

    # 🟢 NEW PATHS
    path('deactivated/', views.customer_deactivated_list, name='customer_deactivated_list'),
    path('<int:customer_id>/reactivate/', views.customer_reactivate, name='customer_reactivate'),
]
