from django.http import HttpResponse
from django.shortcuts import redirect, render


# Create your views here.
def root_redirect(request):
    return redirect('login')

def login_view(request):
    return HttpResponse("Login Page")

def register_view(request):
    return HttpResponse("Register Page")

def forgot_password_view(request):
    return HttpResponse("Forgot Password Page")

def reset_password_view(request, token):
    return HttpResponse(f"Reset Password Token: {token}")

def logout_view(request):
    return redirect('login')
def account_settings(request):
    return HttpResponse("Account Settings Page")
def deactivate_shop(request):
    return HttpResponse("Deactivate Shop Page")
def delete_shop_permanently(request):
    return HttpResponse("Delete Shop Permanently Page")
