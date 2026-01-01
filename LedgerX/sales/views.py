from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction as db_transaction

from .models import Transaction, TransactionItem
from products.models import Product
from customers.models import Customer



# Create your views here.
@login_required
def add_sale(request):
    """
    Handles BOTH:
    - Cash Sale (no customer)
    - Credit Sale (with customer)

    Always creates a Transaction.
    """

    shop = request.user.shop
    products = Product.objects.filter(shop=shop, is_active=True)
    customers = Customer.objects.filter(shop=shop, is_active=True)

    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')  # CASH / CREDIT
        customer = None

        if transaction_type == Transaction.CREDIT:
            customer_id = request.POST.get('customer')
            customer = get_object_or_404(Customer, id=customer_id, shop=shop)

        total_amount = 0
        items_to_create = []

        with db_transaction.atomic():
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
    """
    Adds payment from customer detail page.
    """

    shop = request.user.shop
    customer = get_object_or_404(Customer, id=customer_id, shop=shop)

    if request.method == 'POST':
        amount = request.POST.get('amount')

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
        {'customer': customer}
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

