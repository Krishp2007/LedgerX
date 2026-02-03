from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Sum

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
    qr = get_object_or_404(
        QRToken,
        secure_token=secure_token,
        is_active=True
    )

    customer = qr.customer

    transactions = Transaction.objects.filter(
        customer=customer
    ).order_by('transaction_date')

    ledger_rows = []
    running_balance = 0

    for tx in transactions:
        if tx.transaction_type == 'CREDIT':
            running_balance += tx.total_amount
        elif tx.transaction_type == 'PAYMENT':
            running_balance -= tx.total_amount

        ledger_rows.insert(0, {
            'tx': tx,
            'balance': running_balance,
            'abs_balance': abs(running_balance),  # ✅ added
        })
        

    outstanding_amount = running_balance


    return render(
        request,
        'qr/customer_ledger.html',
        {
            'customer': customer,
            'ledger_rows': ledger_rows,  # 👈 NEW
            'outstanding_amount': outstanding_amount,
            'qr_token': qr,
        }
    )



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


import base64
from io import BytesIO
from django.shortcuts import render

def payment_bridge_view(request):
    """
    Renders the Payment Page with a generated QR Code.
    """
    amount = request.GET.get('amt', 0)
    shop_name = request.GET.get('name', 'Shop')
    
    # 🟢 1. Configuration (Use the ID you provided)
    my_upi = "krishpatel2136@oksbi" 

    # 🟢 2. Construct UPI Link
    upi_link = f"upi://pay?pa={my_upi}&pn={shop_name}&am={amount}&cu=INR&tn=ShopBill"

    # 🟢 3. Generate QR Code Image (Server Side)
    qr = qrcode.make(upi_link)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render(request, 'qr/payment_bridge.html', {
        'amount': amount,
        'shop_name': shop_name,
        'upi_link': upi_link,  # Pass link to template
        'qr_image': img_str    # Pass QR image to template
    })