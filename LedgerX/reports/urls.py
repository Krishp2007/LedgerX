from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('sales/', views.sales_report, name='sales_report'),
    path('products/', views.product_report, name='product_report'),
    path('customers/', views.customer_report, name='customer_report'),
    path('dashboard/', views.dashboard, name='dashboard')
]

