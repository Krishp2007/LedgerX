from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q  # 🟢 Added Q
from django.core.paginator import Paginator # 🟢 Added Paginator

from .models import Customer
from sales.models import Transaction
from qr.models import QRToken


# Create your views here.
@login_required
def customer_list(request):
    shop = request.user.shop
    search_query = request.GET.get('search', '')

    # 1. Get Base Data
    customers_list = Customer.objects.filter(shop=shop, is_active=True).order_by('name')

    # 2. Filter if Search exists
    if search_query:
        customers_list = customers_list.filter(
            Q(name__icontains=search_query) | 
            Q(mobile__icontains=search_query)
        )

    # 3. Paginate (10 items per page)
    paginator = Paginator(customers_list, 10)
    page_number = request.GET.get('page')
    customers = paginator.get_page(page_number)

    return render(
        request,
        'customers/customer_list.html',
        {
            'customers': customers,
            'search_query': search_query
        }
    )
@login_required
def customer_add(request):
    """
    Adds a new credit customer for the shop.
    """

    shop = request.user.shop

    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')

        if not name or not mobile:
            messages.error(request, 'Name and mobile are required')
            return redirect('customer_add')

        # Prevent duplicate customer mobile for same shop
        if Customer.objects.filter(shop=shop, mobile=mobile).exists():
            messages.error(request, 'Customer with this mobile already exists')
            return redirect('customer_add')

        customer = Customer.objects.create(
            shop=shop,
            name=name,
            mobile=mobile
        )

        # Create QR token immediately for transparency
        QRToken.objects.create(customer=customer)

        messages.success(request, 'Customer added successfully')
        return redirect('customer_list')

    return render(request, 'customers/customer_add.html')


@login_required
def customer_detail(request, customer_id):
    shop = request.user.shop

    customer = get_object_or_404(
        Customer,
        id=customer_id,
        shop=shop
    )

    transactions = Transaction.objects.filter(
        customer=customer
    ).order_by('-transaction_date')

    # ✅ Calculate outstanding balance
    credit_total = Transaction.objects.filter(
        customer=customer,
        transaction_type='CREDIT'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    payment_total = Transaction.objects.filter(
        customer=customer,
        transaction_type='PAYMENT'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    outstanding = credit_total - payment_total

    # ✅ GET or CREATE QR token
    qr_token, created = QRToken.objects.get_or_create(
        customer=customer
    )

    return render(
        request,
        'customers/customer_detail.html',
        {
            'customer': customer,
            'transactions': transactions,
            'outstanding': outstanding,
            'qr_token': qr_token,   # 👈 IMPORTANT
        }
    )

@login_required
def customer_edit(request, customer_id):
    """
    Edit customer basic details.
    """

    shop = request.user.shop

    customer = get_object_or_404(
        Customer,
        id=customer_id,
        shop=shop
    )

    if request.method == 'POST':
        customer.name = request.POST.get('name')
        customer.mobile = request.POST.get('mobile')
        customer.save()

        messages.success(request, 'Customer updated successfully')
        return redirect('customer_list')

    return render(
        request,
        'customers/customer_edit.html',
        {'customer': customer}
    )


@login_required
def customer_deactivate(request, customer_id):
    """
    Soft delete customer.
    Ledger & QR remain valid for history.
    """

    shop = request.user.shop

    customer = get_object_or_404(
        Customer,
        id=customer_id,
        shop=shop
    )

    customer.is_active = False
    customer.save()

    messages.info(request, 'Customer deactivated (history preserved)')
    return redirect('customer_list')

