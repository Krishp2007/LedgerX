from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    path('reports/', views.reports_home, name='reports_home'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/products/', views.product_report, name='product_report'),
    path('reports/customers/', views.customer_report, name='customer_report'),
]

