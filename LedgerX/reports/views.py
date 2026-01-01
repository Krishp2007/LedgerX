from django.http import HttpResponse
from django.shortcuts import render

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone

from sales.models import Transaction, TransactionItem
from customers.models import Customer



# Create your views here.
@login_required
def dashboard(request):
    """
    Main dashboard for shopkeeper.
    Shows today's summary + top outstanding customers.
    """

    shop = request.user.shop
    today = timezone.now().date()

    # Today's sales = CASH + CREDIT
    todays_sales = Transaction.objects.filter(
        shop=shop,
        transaction_type__in=['CASH', 'CREDIT'],
        transaction_date__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Today's payments
    todays_payments = Transaction.objects.filter(
        shop=shop,
        transaction_type='PAYMENT',
        transaction_date__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Outstanding calculation
    customers = Customer.objects.filter(shop=shop, is_active=True)

    outstanding_list = []
    total_outstanding = 0

    for customer in customers:
        credit = Transaction.objects.filter(
            customer=customer,
            transaction_type='CREDIT'
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        payment = Transaction.objects.filter(
            customer=customer,
            transaction_type='PAYMENT'
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        balance = credit - payment

        if balance > 0:
            outstanding_list.append({
                'customer': customer,
                'balance': balance
            })
            total_outstanding += balance

    # Top 5 overdue customers
    top_overdue = sorted(
        outstanding_list,
        key=lambda x: x['balance'],
        reverse=True
    )[:5]

    return render(
        request,
        'reports/dashboard.html',
        {
            'todays_sales': todays_sales,
            'todays_payments': todays_payments,
            'total_outstanding': total_outstanding,
            'top_overdue': top_overdue
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
    )

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
    """
    Product-wise sales report.
    Shows how much quantity of each product is sold.
    """

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

    report = items.values(
        'product__name'
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
def customer_report(request):
    """
    Customer outstanding report.
    Shows pending balance for each credit customer.
    """

    shop = request.user.shop
    customers = Customer.objects.filter(shop=shop, is_active=True)

    report = []

    for customer in customers:
        credit = Transaction.objects.filter(
            customer=customer,
            transaction_type='CREDIT'
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        payment = Transaction.objects.filter(
            customer=customer,
            transaction_type='PAYMENT'
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        balance = credit - payment

        if balance > 0:
            report.append({
                'customer': customer,
                'balance': balance
            })

    return render(
        request,
        'reports/customer_report.html',
        {'report': report}
    )



@login_required
def reports_home(request):
    """
    Reports landing page.
    Shows links to different reports.
    """

    return render(request, 'reports/reports_home.html')
