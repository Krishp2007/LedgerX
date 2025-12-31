from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def product_list(request):
    return HttpResponse("Product List")

def product_add(request):
    return HttpResponse("Add Product")

def product_detail(request, product_id):
    return HttpResponse(f"Product Detail: {product_id}")

def product_edit(request, product_id):
    return HttpResponse(f"Edit Product: {product_id}")

def product_deactivate(request, product_id):
    return HttpResponse(f"Delete Product: {product_id}")
