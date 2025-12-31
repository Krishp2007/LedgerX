from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def customer_list(request):
    return HttpResponse("Customer List")

def customer_add(request):
    return HttpResponse("Add Customer")

def customer_detail(request, customer_id):
    return HttpResponse(f"Customer Ledger: {customer_id}")

def customer_edit(request, customer_id):
    return HttpResponse(f"Edit Customer: {customer_id}")

def customer_deactivate(request, customer_id):
    return HttpResponse(f"Deactivate Customer: {customer_id}")
