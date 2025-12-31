from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def customer_ledger_qr(request, secure_token):
    return HttpResponse(f"QR Ledger View: {secure_token}")
