from django.urls import path
from . import views

urlpatterns = [
    
    # Authentication
    path('login/', views.login_view, name='login'),

    # Registration Flow
    path('register/', views.register_view, name='register'),
    path('register/verify/', views.verify_registration_otp_view, name='verify_registration_otp'), # <--- NEW URL

    # 3-Step Password Reset Flow
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('reset-new-password/', views.reset_password_confirm_view, name='reset_password_confirm'),

    path('logout/', views.logout_view, name='logout'),

    # Account / Shop management
    path('account/settings/', views.account_settings, name='account_settings'),
    # path('account/deactivate/', views.deactivate_shop, name='deactivate_shop'),
    path('account/delete/', views.delete_shop_permanently, name='delete_shop_permanently'),
]
