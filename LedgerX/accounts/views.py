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


# def forgot_password_view(request):
#     """
#     Step 1 of OTP-based password reset.
#     - User enters email
#     - System sends 6-digit OTP
#     """

#     if request.method == 'POST':
#         email = request.POST.get('email')

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             messages.error(request, 'No account found with this email')
#             return redirect('forgot_password')

#         # Generate 6-digit OTP
#         otp_code = str(random.randint(100000, 999999))

#         # Store OTP in DB
#         PasswordResetOTP.objects.create(
#             user=user,
#             otp=otp_code
#         )

#         # TODO: Send OTP via Resend API
#         print("DEBUG OTP:", otp_code)

#         messages.success(request, 'OTP sent to your email')
#         return redirect('reset_password')

#     return render(request, 'accounts/forgot_password.html')
# def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        user = User.objects.filter(email=email).first()
        if not user:
            messages.error(request, "No user found with this email")
            return redirect('forgot_password')

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = request.build_absolute_uri(
            reverse('reset_password', args=[uid + '-' + token])
        )

        # For now just print (email later)
        print("RESET LINK:", reset_link)

        messages.success(
            request,
            "Password reset link generated. Check console for link."
        )
        return redirect('login')

    return render(request, 'accounts/forgot_password.html')

from django.urls import reverse
from .models import PasswordResetToken

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email')
            return redirect('forgot_password')

        # ✅ Create reset token
        token = uuid.uuid4()

        PasswordResetToken.objects.create(
            user=user,
            token=token,
            created_at=timezone.now()
        )

        # 🔥 THIS IS THE KEY LINE
        return redirect('reset_password', token=token)

    return render(request, 'accounts/forgot_password.html')

from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password

def reset_password_view(request, token):
    reset = get_object_or_404(
        PasswordResetToken,
        token=token,
        is_used=False
    )

    if request.method == 'POST':
        password = request.POST.get('password')

        reset.user.password = make_password(password)
        reset.user.save()

        reset.is_used = True
        reset.save()

        messages.success(request, "Password reset successful")
        return redirect('login')

    return render(
        request,
        'accounts/reset_password.html',
        {'token': token}
    )

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

