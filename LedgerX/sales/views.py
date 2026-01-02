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
    """
    Handles BOTH:
    - CASH sale (no customer)
    - CREDIT sale (customer required)

    Always creates:
    - Transaction
    - TransactionItems
    Updates:
    - Product stock
    """

    shop = request.user.shop

    # Active products & customers for this shop
    products = Product.objects.filter(shop=shop, is_active=True)
    customers = Customer.objects.filter(shop=shop, is_active=True)

    if request.method == 'POST':
        print("🔥 POST REQUEST RECEIVED")
        print("POST DATA:", request.POST)

        transaction_type = request.POST.get('transaction_type')  # CASH / CREDIT
        customer = None

        # -------------------------------
        # VALIDATE CREDIT CUSTOMER
        # -------------------------------
        if transaction_type == Transaction.CREDIT:
            customer_id = request.POST.get('customer_id')


            if not customer_id:
                messages.error(request, 'Customer is required for credit sale')
                return redirect('add_sale')

            customer = get_object_or_404(
                Customer,
                id=customer_id,
                shop=shop
            )

        total_amount = 0
        items_to_create = []

        # -------------------------------
        # ATOMIC TRANSACTION (VERY IMPORTANT)
        # -------------------------------
        try:
            with db_transaction.atomic():

                # Create empty transaction first
                sale = Transaction.objects.create(
                    shop=shop,
                    customer=customer,              # None for cash sale
                    transaction_type=transaction_type,
                    total_amount=0,                 # Updated later
                    transaction_date=timezone.now()
                )

                # Loop through all products
                for product in products:
                    qty = int(request.POST.get(f'qty_{product.id}', 0))

                    if qty > 0:
                        # Stock validation
                        if product.stock_quantity < qty:
                            raise ValueError(f'Not enough stock for {product.name}')

                        # Reduce stock
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

                # No product selected case
                if not items_to_create:
                    raise ValueError('No products selected')

                # Bulk create items
                TransactionItem.objects.bulk_create(items_to_create)

                # Update final amount
                sale.total_amount = total_amount
                sale.save()

        except ValueError as e:
            messages.error(request, str(e))
            return redirect('add_sale')

        # -------------------------------
        # SUCCESS
        # -------------------------------
        messages.success(request, 'Sale recorded successfully')
        return redirect('transaction_list')

    # -------------------------------
    # GET REQUEST
    # -------------------------------
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
    Adds a payment (no items, no stock change).
    """

    shop = request.user.shop
    customers = Customer.objects.filter(shop=shop, is_active=True)

    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        amount = request.POST.get('amount')

        customer = get_object_or_404(Customer, id=customer_id, shop=shop)

        Transaction.objects.create(
            shop=shop,
            customer=customer,
            transaction_type=Transaction.PAYMENT,
            total_amount=amount,
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

