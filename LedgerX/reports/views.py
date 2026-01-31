from django.http import HttpResponse
from django.shortcuts import render

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone

from products.models import Product  # 🟢 Added Import

from sales.models import Transaction, TransactionItem
from customers.models import Customer

from itertools import chain
from operator import attrgetter


# Create your views here.
@login_required
def dashboard(request):
    """
    Main dashboard: Summary Cards + Recent Activity.
    Optimized to show actionable metrics (Low Stock, Active Customers) 
    instead of heavy financial calculations.
    """
    shop = request.user.shop
    today = timezone.localtime(timezone.now()).date()

    # 1. Today's Sales (Invoice Value: CASH + CREDIT)
    todays_sales = Transaction.objects.filter(
        shop=shop,
        transaction_type__in=['CASH', 'CREDIT'],
        transaction_date__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # 2. Today's Inflow (Money In: PAYMENT + CASH)
    todays_payments = Transaction.objects.filter(
        shop=shop,
        transaction_type__in=['PAYMENT', 'CASH'],
        transaction_date__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # 3. 🟢 NEW METRICS (Actionable & Fast)
    
    # Low Stock: Count products with less than 10 quantity
    low_stock_count = Product.objects.filter(
        shop=shop, 
        stock_quantity__lt=10
    ).count()
    
    # Total Active Customers
    total_customers = Customer.objects.filter(
        shop=shop, 
        is_active=True
    ).count()

    # 4. Recent Activity (Transactions + New Customers mixed)
    recent_txns = Transaction.objects.filter(shop=shop).select_related('customer').order_by('-created_at')[:5]
    recent_custs = Customer.objects.filter(shop=shop).order_by('-created_at')[:5]

    # Combine and sort by newest first
    recent_activities = sorted(
        chain(recent_txns, recent_custs),
        key=attrgetter('created_at'),
        reverse=True
    )[:5]

    return render(
        request,
        'reports/dashboard.html',
        {
            'todays_sales': todays_sales,
            'todays_payments': todays_payments,
            'low_stock_count': low_stock_count,      # 🟢 New Variable
            'total_customers': total_customers,      # 🟢 New Variable
            'recent_activities': recent_activities,
        }
    )

@login_required
def customer_report(request):
    shop = request.user.shop
    # Check filter type: 'outstanding' (default) or 'advance'
    report_type = request.GET.get('type', 'outstanding') 

    customers = Customer.objects.filter(shop=shop, is_active=True)
    report = []

    for customer in customers:
        credit = Transaction.objects.filter(customer=customer, transaction_type='CREDIT').aggregate(total=Sum('total_amount'))['total'] or 0
        payment = Transaction.objects.filter(customer=customer, transaction_type='PAYMENT').aggregate(total=Sum('total_amount'))['total'] or 0
        balance = credit - payment

        if report_type == 'outstanding' and balance > 0:
            report.append({'customer': customer, 'balance': balance})
        elif report_type == 'advance' and balance < 0:
            report.append({'customer': customer, 'balance': abs(balance)})

    return render(
        request,
        'reports/customer_report.html',
        {
            'report': report,
            'report_type': report_type # Pass type to template
        }
    )

@login_required
def sales_report(request):
    """
    Sales report between selected dates.
    Includes CASH + CREDIT transactions only.
    """

    shop = request.user.shop
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    transactions = Transaction.objects.filter(
        shop=shop,
        transaction_type__in=['CASH', 'CREDIT']
    ).order_by('-transaction_date')

    if start_date and end_date:
        transactions = transactions.filter(
            transaction_date__date__range=[start_date, end_date]
        )

    total_sales = transactions.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    return render(
        request,
        'reports/sales_report.html',
        {
            'transactions': transactions,
            'total_sales': total_sales,
            'start_date': start_date,
            'end_date': end_date
        }
    )


@login_required
def product_report(request):
    shop = request.user.shop
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    items = TransactionItem.objects.filter(
        transaction__shop=shop,
        transaction__transaction_type__in=['CASH', 'CREDIT']
    )

    if start_date and end_date:
        items = items.filter(
            transaction__transaction_date__date__range=[start_date, end_date]
        )

    # 🟢 CHANGED: Added 'product__id' to values() so we can link to details
    report = items.values(
        'product__name', 
        'product__id' 
    ).annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')

    return render(
        request,
        'reports/product_report.html',
        {
            'report': report,
            'start_date': start_date,
            'end_date': end_date
        }
    )


@login_required
def reports_home(request):
    """
    Reports landing page.
    Shows links to different reports.
    """

    return render(request, 'reports/reports_home.html')
