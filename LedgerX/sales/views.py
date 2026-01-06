from decimal import Decimal,ROUND_HALF_UP
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction as db_transaction
from django.db.models import Sum


from .models import Transaction, TransactionItem
from products.models import Product
from customers.models import Customer



# Create your views here.
@login_required
def add_sale(request):
    shop = request.user.shop
    products = Product.objects.filter(shop=shop, is_active=True)
    customers = Customer.objects.filter(shop=shop, is_active=True)

    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        customer_id = request.POST.get('customer_id')
        customer = None
        
        if transaction_type == 'CREDIT' and customer_id:
            customer = get_object_or_404(Customer, id=customer_id, shop=shop)

        # Securely capture the paid amount as a Decimal
        raw_paid = request.POST.get('amount_paid', '0')
        paid_today = Decimal(str(raw_paid)) if raw_paid else Decimal('0')

        total_bill = Decimal('0')
        items_to_create = []

        with db_transaction.atomic():
            # 1️⃣ Create Sale with both values
            # Inside add_sale view
            sale = Transaction.objects.create(
                shop=shop,
                customer=customer,
                transaction_type=transaction_type,
                total_amount=0, 
                paid_amount=paid_today,  # This will no longer crash after migration
                transaction_date=timezone.now()
)

            for product in products:
                qty = int(request.POST.get(f'qty_{product.id}', 0))
                if qty > 0:
                    product.stock_quantity -= qty
                    product.save()
                    total_bill += Decimal(qty) * product.default_price
                    
                    items_to_create.append(TransactionItem(
                        transaction=sale, product=product, 
                        quantity=qty, price_at_sale=product.default_price
                    ))

            TransactionItem.objects.bulk_create(items_to_create)
            
            # 2️⃣ Update the final total
            sale.total_amount = total_bill
            sale.save()

            # Optional: Still create a separate PAYMENT entry for the ledger history
            if paid_today > 0:
                Transaction.objects.create(
                    shop=shop, customer=customer, transaction_type='PAYMENT',
                    total_amount=paid_today, transaction_date=timezone.now()
                )

        messages.success(request, 'Sale recorded successfully')
        return redirect('transaction_list')

    return render(request, 'sales/add_sale.html', {'products': products, 'customers': customers})

@login_required
def add_payment(request):
    """
    Adds a payment (no items, no stock change).
    """

    shop = request.user.shop
    customers = Customer.objects.filter(shop=shop, is_active=True)

    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        customer = get_object_or_404(Customer, id=customer_id, shop=shop)
        amount = request.POST.get('amount')
        if amount:
            # Always cast to Decimal for money!
            Transaction.objects.create(
                shop=shop,
                customer=customer,
                transaction_type=Transaction.PAYMENT,
                total_amount=Decimal(str(amount)), # THIS ensures it acts as a "positive" payment
                paid_amount=Decimal('0'),
                transaction_date=timezone.now()
            )

        messages.success(request, 'Payment recorded successfully')
        return redirect('transaction_list')

    return render(
        request,
        'sales/add_payment.html',
        {'customers': customers}
    )


@login_required
def add_payment_for_customer(request, customer_id):
    shop = request.user.shop

    customer = get_object_or_404(
        Customer,
        id=customer_id,
        shop=shop,
        is_active=True
    )

    # Calculate outstanding
    credit_total = Transaction.objects.filter(
        customer=customer,
        transaction_type=Transaction.CREDIT
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    payment_total = Transaction.objects.filter(
        customer=customer,
        transaction_type=Transaction.PAYMENT
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    outstanding = credit_total - payment_total

    if request.method == 'POST':
        amount = request.POST.get('amount')

        if not amount or float(amount) <= 0:
            messages.error(request, 'Invalid payment amount')
            return redirect('add_payment_for_customer', customer_id=customer.id)

        Transaction.objects.create(
            shop=shop,
            customer=customer,
            transaction_type=Transaction.PAYMENT,
            total_amount=amount,
            transaction_date=timezone.now()
        )

        messages.success(request, 'Payment recorded successfully')
        return redirect('customer_detail', customer_id=customer.id)

    return render(
        request,
        'sales/add_payment_for_customer.html',
        {
            'customer': customer,
            'outstanding': outstanding
        }
    )


@login_required
def transaction_list(request):
    """
    Shows all transactions for the logged-in shop.
    """

    shop = request.user.shop

    transactions = Transaction.objects.filter(
        shop=shop,
        is_active=True
    ).order_by('-transaction_date')

    return render(
        request,
        'sales/transaction_list.html',
        {'transactions': transactions}
    )


@login_required
def transaction_detail(request, transaction_id):
    """
    Shows details of a single transaction.
    - Sales show items
    - Payments show amount only
    """

    shop = request.user.shop

    transaction_obj = get_object_or_404(
        Transaction,
        id=transaction_id,
        shop=shop
    )

    return render(
        request,
        'sales/transaction_detail.html',
        {'transaction': transaction_obj}
    )

