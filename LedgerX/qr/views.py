from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Sum

from .models import QRToken
from sales.models import Transaction

# Create your views here.
def customer_ledger_qr(request, secure_token):
    """
    Public, read-only customer ledger view.
    Accessed via QR code.
    No authentication required.
    """

    # 1. Validate QR token
    qr = get_object_or_404(
        QRToken,
        secure_token=secure_token,
        is_active=True
    )

    # 2. Check expiry (if expiry is set)
    if qr.expires_at and qr.expires_at < timezone.now():
        return HttpResponse("This QR code has expired.")

    customer = qr.customer

    # 3. Fetch all transactions for this customer
    transactions = Transaction.objects.filter(
        customer=customer
    ).order_by('transaction_date')

    # 4. Calculate outstanding balance
    credit_total = Transaction.objects.filter(
        customer=customer,
        transaction_type='CREDIT'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    payment_total = Transaction.objects.filter(
        customer=customer,
        transaction_type='PAYMENT'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    outstanding = credit_total - payment_total

    # 5. Render read-only ledger
    return render(
        request,
        'qr/customer_ledger.html',
        {
            'customer': customer,
            'transactions': transactions,
            'outstanding': outstanding
        }
    )

