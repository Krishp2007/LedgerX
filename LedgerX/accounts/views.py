import uuid
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
import random

from django.contrib.auth.tokens import default_token_generator

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

from .models import Shop
from .models import PasswordResetOTP   # OTP model (shown below)


# Create your views here.


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


import random
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from .models import Shop, PasswordResetOTP  # Make sure you uncomment PasswordResetOTP in models.py

# accounts/views.py

# accounts/views.py

import re # For regex checking
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

def register_view(request):
    # Default: Empty form data
    form_data = {} 

    if request.method == 'POST':
        # Capture what the user typed
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        shop_name = request.POST.get('shop_name')
        owner_name = request.POST.get('owner_name')

        # Store it to send back if there's an error
        form_data = {
            'username': username,
            'email': email,
            'shop_name': shop_name,
            'owner_name': owner_name
            # We rarely send 'password' back for security reasons
        }

        # --- 🛡️ 1. EMAIL VALIDATION ---
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email address format.')
            return render(request, 'accounts/register.html', {'form_data': form_data})

        # --- 🛡️ 2. PASSWORD VALIDATION ---
        try:
            validate_password(password)
            if not re.search(r'[A-Z]', password):
                raise ValidationError("Password must contain at least one uppercase letter.")
            if not re.search(r'[0-9]', password):
                raise ValidationError("Password must contain at least one number.")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError("Password must contain at least one special character (!@#$).")
        except ValidationError as e:
            error_msg = str(e.messages[0]) if hasattr(e, 'messages') else str(e)
            messages.error(request, error_msg)
            return render(request, 'accounts/register.html', {'form_data': form_data})

        # --- 🛡️ 3. DUPLICATE CHECKS ---
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/register.html', {'form_data': form_data})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered. Please login.')
            return render(request, 'accounts/register.html', {'form_data': form_data})

        # --- SUCCESS: PROCEED TO OTP ---
        otp_code = str(random.randint(100000, 999999))
        
        request.session['register_data'] = {
            'username': username, 'email': email, 'password': password,
            'shop_name': shop_name, 'owner_name': owner_name, 'otp': otp_code
        }

        # Send Email Logic (Kept same as before)
        context = {'otp': otp_code, 'username': username}
        html_message = render_to_string('emails/register_otp.html', context)
        plain_message = strip_tags(html_message)

        try:
            send_mail("Verify Your LedgerX Account", plain_message, settings.EMAIL_HOST_USER, [email], html_message=html_message, fail_silently=False)
            messages.success(request, f"OTP sent to {email}")
            return redirect('verify_registration_otp')
        except Exception as e:
            messages.error(request, f"Error sending email: {e}")
            return redirect('register')

    return render(request, 'accounts/register.html', {'form_data': form_data})

def verify_registration_otp_view(request):
    # Get data from session
    data = request.session.get('register_data')

    if not data:
        messages.error(request, "Session expired. Please register again.")
        return redirect('register')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')

        if otp_input == data['otp']:
            # 1. Create User
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )

            # 2. Create Shop
            shop = Shop.objects.create(
                user=user,
                shop_name=data['shop_name'],
                owner_name=data['owner_name']
            )

            # 3. Login User
            login(request, user)

            # --- 📧 SEND WELCOME EMAIL ---
            try:
                context = {
                    'owner_name': data['owner_name'],
                    'shop_name': data['shop_name']
                }
                html_message = render_to_string('emails/welcome.html', context)
                plain_message = strip_tags(html_message)

                send_mail(
                    subject=f"Welcome to LedgerX, {data['shop_name']}!",
                    message=plain_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[data['email']],
                    html_message=html_message,
                    fail_silently=True  # If this fails, don't crash the registration
                )
            except Exception as e:
                print(f"Welcome email failed: {e}")
            # -----------------------------

            # 4. Cleanup Session
            del request.session['register_data']

            messages.success(request, "Account verified! Welcome to your Dashboard.")
            return redirect('dashboard')
        
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'accounts/verify_registration.html', {'email': data['email']})


# accounts/views.py (Partial Update - Add/Replace these functions)

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            
            # 1. Generate OTP
            otp_code = str(random.randint(100000, 999999))
            
            # 2. Save OTP (Delete old ones first to avoid clutter)
            PasswordResetOTP.objects.filter(user=user).delete()
            PasswordResetOTP.objects.create(user=user, otp=otp_code)

            # 3. Send Email
            context = {'otp': otp_code}
            html_message = render_to_string('emails/password_reset.html', context)
            plain_message = strip_tags(html_message)

            send_mail(
                subject="Reset Your LedgerX Password",
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False
            )
            
            # 4. Save email in session to know WHO we are verifying
            request.session['reset_email'] = email
            messages.success(request, f"OTP Code sent to {email}")
            return redirect('verify_otp')

        except User.DoesNotExist:
            messages.error(request, "This email is not registered with us.")
            # Returns 200 OK because we render the page again to show the error
            return render(request, 'accounts/forgot_password.html')

    return render(request, 'accounts/forgot_password.html')


def verify_otp_view(request):
    # Get the email we stored in step 1
    email = request.session.get('reset_email')
    
    if not email:
        messages.error(request, "Session expired. Please try again.")
        return redirect('forgot_password')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        
        try:
            user = User.objects.get(email=email)
            # Check if OTP matches the latest one in DB
            saved_otp = PasswordResetOTP.objects.filter(user=user, otp=otp_input).first()

            if saved_otp:
                # Success! Mark as verified in session
                request.session['otp_verified'] = True
                saved_otp.delete() # Cleanup
                return redirect('reset_password_confirm')
            else:
                messages.error(request, "Invalid OTP Code. Please try again.")

        except User.DoesNotExist:
             messages.error(request, "User not found.")

    return render(request, 'accounts/verify_otp.html')


def reset_password_confirm_view(request):
    email = request.session.get('reset_email')
    is_verified = request.session.get('otp_verified')

    # Security Check: Don't let them skip the OTP step!
    if not email or not is_verified:
        messages.error(request, "Unauthorized access. Please verify OTP first.")
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            # Change Password
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()

            # Clean Session
            del request.session['reset_email']
            del request.session['otp_verified']

            messages.success(request, "Password changed successfully! Please Login.")
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

