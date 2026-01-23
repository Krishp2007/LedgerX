from django.shortcuts import render, redirect

def root_view(request):
    """
    Smart root:
    - If logged in → dashboard
    - Else → home page
    """
    if request.user.is_authenticated:
        return redirect('dashboard')  # Dashboard
    return render(request, 'public/home.html')


def about(request):
    return render(request, 'public/about.html')


def contact(request):
    return render(request, 'public/contact.html')


from django.core.mail import EmailMessage
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def contact_ajax(request):
    try:
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email or not message:
            return JsonResponse(
                {"success": False, "error": "All fields are required."},
                status=400
            )

        # ✅ EMAIL 1: To LedgerX support
        support_email = EmailMessage(
            subject=f"New Contact Message from {name}",
            body=f"""
You have received a new contact message.

Name: {name}
Email: {email}

Message:
{message}
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=["Krishp2163@gmail.com"],
            reply_to=[email],  # 👈 NOW THIS WORKS
        )
        support_email.send(fail_silently=False)

        # ✅ EMAIL 2: Confirmation to user
        user_email = EmailMessage(
            subject="We received your message – LedgerX",
            body=f"""
Hi {name},

Thank you for contacting LedgerX.

We’ve received your message and our team will get back to you shortly.

Your message:
--------------------
{message}
--------------------

If you didn’t send this message, you can safely ignore this email.

Regards,
LedgerX Support Team
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        user_email.send(fail_silently=False)

        print("CONTACT EMAILS SENT SUCCESSFULLY")

        return JsonResponse({"success": True})

    except Exception as e:
        print("CONTACT EMAIL ERROR:", e)
        return JsonResponse(
            {"success": False, "error": "Something went wrong. Please try again later."},
            status=500
        )
