from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def add_sale(request):
    return HttpResponse("Add Sale (Cash / Credit)")

def add_payment(request):
    return HttpResponse("Add Payment")

def add_payment_for_customer(request, customer_id):
    return HttpResponse(f"Add Payment for Customer {customer_id}")

def transaction_list(request):
    return HttpResponse("Transaction List")

def transaction_detail(request, transaction_id):
    return HttpResponse(f"Transaction Detail: {transaction_id}")
