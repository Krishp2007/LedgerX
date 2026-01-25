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
        customer = None

        if transaction_type == Transaction.CREDIT:
            customer_id = request.POST.get('customer_id')
            customer = get_object_or_404(Customer, id=customer_id, shop=shop)

        amount_paid = request.POST.get('amount_paid')
        amount_paid = float(amount_paid) if amount_paid else 0

        total_amount = 0
        items_to_create = []

        with db_transaction.atomic():

            # 1️⃣ Create SALE (CASH or CREDIT)
            sale = Transaction.objects.create(
                shop=shop,
                customer=customer,
                transaction_type=transaction_type,
                total_amount=0,
                transaction_date=timezone.now()
            )

            for product in products:
                qty = int(request.POST.get(f'qty_{product.id}', 0))

                if qty > 0:
                    if product.stock_quantity < qty:
                        messages.error(request, f'Not enough stock for {product.name}')
                        raise Exception("Insufficient stock")

                    product.stock_quantity -= qty
                    product.save()

                    line_total = qty * product.default_price
                    total_amount += line_total

                    items_to_create.append(
                        TransactionItem(
                            transaction=sale,
                            product=product,
                            quantity=qty,
                            price_at_sale=product.default_price
                        )
                    )

            if not items_to_create:
                messages.error(request, 'No products selected')
                return redirect('add_sale')

            TransactionItem.objects.bulk_create(items_to_create)

            sale.total_amount = total_amount
            sale.save()

            # 2️⃣ CREATE PAYMENT IF AMOUNT PAID > 0
            if amount_paid > 0:
                Transaction.objects.create(
                    shop=shop,
                    customer=customer,
                    transaction_type=Transaction.PAYMENT,
                    total_amount=amount_paid,
                    transaction_date=timezone.now()
                )

        messages.success(request, 'Sale recorded successfully')
        return redirect('transaction_list')

    return render(
        request,
        'sales/add_sale.html',
        {
            'products': products,
            'customers': customers
        }
    )


@login_required
def add_payment(request):
    """
    Handles 'Add Payment' from the Dashboard (Dropdown Selection).
    """
    shop = request.user.shop
    customers = Customer.objects.filter(shop=shop, is_active=True)

    if request.method == 'POST':
        customer_id = request.POST.get('customer') # Get ID from dropdown
        amount = request.POST.get('amount')

        # 1. Check if empty
        if not customer_id:
            messages.error(request, "Please select a customer from the list.")
            return render(request, 'sales/add_payment.html', {'customers': customers})

        # 2. Try to find the customer (Crash-Proof Way)
        try:
            customer_obj = Customer.objects.get(id=customer_id, shop=shop)
        except (Customer.DoesNotExist, ValueError):
            messages.error(request, "Error: Selected customer not found.")
            return redirect('add_payment')

        # 3. Save
        try:
            Transaction.objects.create(
                shop=shop,
                customer=customer_obj,
                transaction_type='PAYMENT',
                total_amount=amount
            )
            messages.success(request, f"Payment of ₹{amount} received from {customer_obj.name}.")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"Error saving payment: {e}")
            return redirect('add_payment')

    return render(request, 'sales/add_payment.html', {'customers': customers})

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
    Shows a LIST of transactions.
    Used by Dashboard Cards (Today's Sales, Payments, etc.)
    Does NOT require an ID.
    """
    shop = request.user.shop
    transactions = Transaction.objects.filter(shop=shop).order_by('-created_at')

    # 🔍 FILTER: Date (e.g., ?date=today)
    date_filter = request.GET.get('date')
    if date_filter == 'today':
        today = timezone.localtime(timezone.now()).date()
        transactions = transactions.filter(transaction_date__date=today)

    # 🔍 FILTER: Transaction Type (e.g., ?type=CASH,CREDIT)
    type_filter = request.GET.get('type')
    if type_filter:
        types = type_filter.split(',')
        transactions = transactions.filter(transaction_type__in=types)

    return render(request, 'sales/transaction_list.html', {'transactions': transactions})

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

