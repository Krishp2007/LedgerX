from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
import random

from .models import Shop
from .models import PasswordResetOTP   # OTP model (shown below)


# Create your views here.
def root_redirect(request):
    """
    Root URL handler.
    - If logged in → dashboard
    - Else → login page
    """

    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    """
    Logs user in using Django authentication.
    """

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        messages.error(request, 'Invalid username or password')
        return redirect('login')

    return render(request, 'accounts/login.html')


def register_view(request):
    """
    Registers a new shopkeeper.
    Creates:
    - Django User (email + password)
    - Shop linked to that user
    Automatically logs user in.
    """

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        shop_name = request.POST.get('shop_name')
        owner_name = request.POST.get('owner_name')

        # Prevent duplicate usernames
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        # Create User (AUTH DATA)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create Shop (BUSINESS DATA)
        Shop.objects.create(
            user=user,
            shop_name=shop_name,
            owner_name=owner_name
        )

        # Auto-login after registration
        login(request, user)

        return redirect('dashboard')

    return render(request, 'accounts/register.html')


def forgot_password_view(request):
    """
    Step 1 of OTP-based password reset.
    - User enters email
    - System sends 6-digit OTP
    """

    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email')
            return redirect('forgot_password')

        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))

        # Store OTP in DB
        PasswordResetOTP.objects.create(
            user=user,
            otp=otp_code
        )

        # TODO: Send OTP via Resend API
        print("DEBUG OTP:", otp_code)

        messages.success(request, 'OTP sent to your email')
        return redirect('reset_password')

    return render(request, 'accounts/forgot_password.html')


def reset_password_view(request):
    """
    Step 2 of OTP-based password reset.
    - Verify OTP
    - Set new password
    """

    if request.method == 'POST':
        email = request.POST.get('email')
        otp_entered = request.POST.get('otp')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('reset_password')

        try:
            user = User.objects.get(email=email)
            otp_obj = PasswordResetOTP.objects.filter(
                user=user,
                otp=otp_entered,
                is_used=False
            ).latest('created_at')
        except:
            messages.error(request, 'Invalid or expired OTP')
            return redirect('reset_password')

        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()

        # Set new password securely
        user.set_password(new_password)
        user.save()

        messages.success(request, 'Password reset successful. Please login.')
        return redirect('login')

    return render(request, 'accounts/reset_password.html')


@login_required
def logout_view(request):
    """
    Logs out the current user.
    """

    logout(request)
    return redirect('login')

@login_required
def account_settings(request):
    """
    Account settings page.
    Shows shop info, delete account option, etc.
    """

    shop = request.user.shop
    return render(request, 'accounts/account_settings.html', {'shop': shop})

# def deactivate_shop(request):
#     return HttpResponse("Deactivate Shop Page")
@login_required
def delete_shop_permanently(request):
    """
    Permanently deletes user and all related data.
    Requires password confirmation.
    """

    if request.method == 'POST':
        password = request.POST.get('password')
        user = request.user

        # Verify password before deletion
        auth_user = authenticate(username=user.username, password=password)

        if auth_user is None:
            messages.error(request, 'Incorrect password')
            return redirect('delete_shop_permanently')

        # Hard delete (cascade)
        user.delete()

        messages.warning(request, 'Your account and all data have been deleted.')
        return redirect('login')

    return render(request, 'accounts/delete_account_confirm.html')

