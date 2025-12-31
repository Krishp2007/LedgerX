from django.urls import path
from . import views

urlpatterns = [
    # Root handling
    path('', views.root_redirect, name='root'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password_view, name='reset_password'),
    path('logout/', views.logout_view, name='logout'),

    # Account / Shop management
    path('account/settings/', views.account_settings, name='account_settings'),
    path('account/deactivate/', views.deactivate_shop, name='deactivate_shop'),
    path('account/delete/', views.delete_shop_permanently, name='delete_shop_permanently'),
]
