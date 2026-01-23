from django.urls import path
from . import views

urlpatterns = [
    

    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.password_reset_request, name='password_reset'),
    path('reset-verify/', views.password_reset_verify, name='password_reset_verify'),
    path('logout/', views.logout_view, name='logout'),
    # Account / Shop management
    path('account/settings/', views.account_settings, name='account_settings'),
    # path('account/deactivate/', views.deactivate_shop, name='deactivate_shop'),
    path('account/delete/', views.delete_shop_permanently, name='delete_shop_permanently'),
]
