import requests
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


from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string


# --- 🛠️ HELPER: Send Email via BREVO API (Same as Accounts) ---
def send_email_via_api(to_email, subject, html_content, reply_to_email=None, reply_to_name=None):
    url = "https://api.brevo.com/v3/smtp/email"
    
    # Base Payload
    payload = {
        "sender": {
            "name": "LedgerX",
            "email": settings.DEFAULT_FROM_EMAIL
        },
        "to": [
            {
                "email": to_email
            }
        ],
        "subject": subject,
        "htmlContent": html_content
    }

    # Add Reply-To if provided (Crucial for Contact Form)
    if reply_to_email:
        payload["replyTo"] = {
            "email": reply_to_email,
            "name": reply_to_name if reply_to_name else "User"
        }

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in [200, 201, 202]:
            return True
        else:
            print(f"Brevo Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Brevo Connection Error: {e}")
        return False

@require_POST
def contact_ajax(request):
    try:
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email or not message:
            return JsonResponse({"success": False, "error": "All fields are required."}, status=400)

        # ✅ EMAIL 1: Support Alert (To LedgerX Team)
        # 🟢 FIX: Send TO the default email (ledgerx.team), not the hardcoded one.
        support_html = render_to_string('emails/contact_support.html', {
            'name': name,
            'email': email,
            'message': message
        })

        send_email_via_api(
            to_email=settings.DEFAULT_FROM_EMAIL,  # <--- SENDS TO ledgerx.team@gmail.com
            subject=f"New Contact: {name}",
            html_content=support_html,
            reply_to_email=email,
            reply_to_name=name
        )

        # ✅ EMAIL 2: Confirmation (To User)
        user_html = render_to_string('emails/contact_user_confirmation.html', {
            'name': name,
            'message': message
        })

        send_email_via_api(
            to_email=email,
            subject="We received your message – LedgerX",
            html_content=user_html
        )

        return JsonResponse({"success": True})

    except Exception as e:
        print("CONTACT ERROR:", e)
        return JsonResponse({"success": False, "error": "Server Error"}, status=500)