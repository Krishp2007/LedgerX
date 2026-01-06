from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from .models import QRToken
from sales.models import Transaction

import qrcode
from io import BytesIO
from django.urls import reverse

from .models import QRToken

def generate_qr_image(request, customer_id):
    """
    Generates QR image for a customer's ledger.
    Returns PNG image.
    """

    qr_token = get_object_or_404(
        QRToken,
        customer__id=customer_id
    )

    # Absolute ledger URL
    ledger_url = request.build_absolute_uri(
        reverse('customer_ledger_qr', args=[qr_token.secure_token])
    )

    # Generate QR
    qr = qrcode.make(ledger_url)

    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)

    return HttpResponse(buffer, content_type='image/png')

def customer_ledger_qr(request, secure_token):
    qr = get_object_or_404(QRToken, secure_token=secure_token, is_active=True)
    customer = qr.customer
    transactions = Transaction.objects.filter(customer=customer).order_by('transaction_date')

    ledger_rows = []
    running_balance = Decimal('0.00')

    for tx in transactions:
        if tx.transaction_type == 'CREDIT':
            # Balance increases by Total, then decreases by the upfront paid_amount
            running_balance += (tx.total_amount - tx.paid_amount)
        elif tx.transaction_type == 'PAYMENT':
            # Balance decreases by standalone payments
            running_balance -= tx.total_amount

        ledger_rows.insert(0, {
            'tx': tx,
            'balance': running_balance,
            'abs_balance': abs(running_balance),
        })

    return render(request, 'qr/customer_ledger.html', {
        'customer': customer,
        'ledger_rows': ledger_rows,
        'outstanding_amount': running_balance,
        'qr_token': qr,
    })


def qr_transaction_detail(request, secure_token, transaction_id):
    qr = get_object_or_404(
        QRToken,
        secure_token=secure_token,
        is_active=True
    )

    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        customer=qr.customer
    )

    items = []
    for item in transaction.items.all():
        items.append({
            'product': item.product,
            'quantity': item.quantity,
            'price': item.price_at_sale,
            'line_total': item.quantity * item.price_at_sale,  # ✅ calculated here
        })

    return render(
        request,
        'qr/transaction_detail.html',
        {
            'transaction': transaction,
            'customer': qr.customer,
            'items': items,  # 👈 pass pre-calculated data
        }
    )
