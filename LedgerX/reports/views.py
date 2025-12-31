from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def dashboard(request):
    return HttpResponse("Dashboard")

def sales_report(request):
    return HttpResponse("Sales Report")

def product_report(request):
    return HttpResponse("Product Analytics")

def customer_report(request):
    return HttpResponse("Customer Report")
