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
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from .models import PasswordResetToken
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
import random

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

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email')
        # Generate a random 6-digit OTP
        otp = random.randint(100000, 999999)
        
        # In a real app, you would save this OTP to the database 
        # or session to verify it in the next step.
        request.session['reset_otp'] = otp
        request.session['reset_email'] = email

        subject = "Your Password Reset OTP"
        message = f"Your OTP for resetting your password is: {otp}"
        from_email = settings.DEFAULT_FROM_EMAIL
        
        try:
            send_mail(subject, message, from_email, [email])
            messages.success(request, "OTP sent to your email/phone successfully.")
            # return redirect('verify_otp') # Redirect to your verification page
        except Exception as e:
            messages.error(request, "Error sending email. Check your SMTP settings.")
            
    return render(request, "accounts/forgot_password.html") # Change to your actual template path

# def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            # Generate a random 6-digit OTP
            otp = random.randint(100000, 999999)
            
            # Store in session
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email

            # Send Email
            subject = "Your Password Reset OTP"
            message = f"Your OTP for resetting your password is: {otp}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
            
            messages.success(request, "OTP sent to your email successfully.")
            # ✅ CORRECT: Redirect to the URL NAME from urls.py
            return redirect('password_reset_verify') 
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email')
            return redirect('forgot_password')
        except Exception as e:
            messages.error(request, "Error sending email. Check SMTP settings.")
            return redirect('forgot_password')
            
    return render(request, 'accounts/forgot_password.html')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        # Use iexact to avoid case-sensitivity issues
        user = User.objects.filter(email__iexact=email).first()

        if user:
            # 1. Generate OTP
            otp = random.randint(100000, 999999)
            
            # 2. Store in Session
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email
            
            # Print to terminal so you can see it if the email is slow
            print(f"DEBUG: OTP for {email} is {otp}") 

            # 3. Send Email
            subject = "Your Password Reset OTP"
            message = f"Your OTP for resetting your password is: {otp}"
            
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                messages.success(request, "OTP sent successfully!")
            except Exception as e:
                print(f"SMTP Error: {e}")
                messages.warning(request, "Email failed to send, but check terminal for OTP.")

            # ✅ FIX: Redirect to the URL NAME, not the HTML file path
            return redirect('password_reset_verify') 
        else:
            messages.error(request, "No account found with this email.")
            return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')

def password_reset_verify(request):
    if request.method == "POST":
        username = request.POST.get('username')
        otp_entered = request.POST.get('otp')
        new_password = request.POST.get('new_password')

        session_otp = request.session.get('reset_otp')
        session_email = request.session.get('reset_email')

        if str(otp_entered) == str(session_otp):
            try:
                user = User.objects.get(username=username, email__iexact=session_email)
                user.set_password(new_password)
                user.save()
                
                # Cleanup session
                del request.session['reset_otp']
                del request.session['reset_email']
                
                messages.success(request, "Password updated successfully!")
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, "Username does not match this email.")
        else:
            messages.error(request, "Invalid OTP.")
            
    # ✅ FIX: Added .html extension
    return render(request, 'accounts/password_reset_verify.html')
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

