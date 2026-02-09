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
import urllib.parse
from django.shortcuts import render
from customers.models import Customer

def payment_bridge_view(request):
    """
    Renders the Payment Page.
    - Uses 'Shop Name' for visual display on the HTML page.
    - Uses 'Owner Name' for the UPI Link (to match Bank Records).
    """
    # 1. Get Parameters
    amount_raw = request.GET.get('amt', '0')
    customer_id = request.GET.get('cid') 
    
    # Defaults
    shop_upi_id = "example@upi"
    display_name = request.GET.get('name', 'Shop') # Visual Name
    banking_name = "Shop Owner"                    # Bank Name

    if customer_id:
        customer = get_object_or_404(Customer, id=customer_id)
        shop = customer.shop
        
        # 🟢 1. Visual Name (e.g. "Chintu Sweets")
        display_name = shop.shop_name 
        
        # 🟢 2. Banking Name (e.g. "Krish Patel") - Matches Bank Account
        banking_name = shop.owner_name 

        if shop.upi_id:
            shop_upi_id = shop.upi_id

    # 3. Strict Amount Formatting ("500" -> "500.00")
    try:
        amount_formatted = "{:.2f}".format(float(amount_raw))
    except ValueError:
        amount_formatted = "0.00"

    # 4. URL Encoding
    # We encode the OWNER NAME for the UPI link because that matches the bank.
    banking_name_encoded = urllib.parse.quote(banking_name)
    note_encoded = urllib.parse.quote("Shop Bill")

    # 5. Construct UPI Link
    # pa = UPI ID
    # pn = Owner Name (Best chance of matching bank record)
    # am = Strict Amount
    upi_link = f"upi://pay?pa={shop_upi_id}&pn={banking_name_encoded}&am={amount_formatted}&cu=INR&tn={note_encoded}"

    # 6. Generate QR Code
    qr = qrcode.make(upi_link)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

    context = {
        'amount': amount_raw,
        'shop_name': display_name,  # Shows "Chintu Sweets" on the website
        'upi_link': upi_link,       # Sends "Krish Patel" to the App
        'qr_image': img_str
    }
    
    if customer_id:
         context['customer'] = customer

    return render(request, 'qr/payment_bridge.html', context)