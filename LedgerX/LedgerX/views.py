from django.shortcuts import render
from django.http import HttpResponse

def home(request):
  return render(request, 'index.html')

def about(request):
  return HttpResponse("<h1>Welcome to Chai's Django Project: About page</h1>")

def contact(request):
  return HttpResponse("<h1>Welcome to Chai's Django Project: Contact page</h1>")
    # return render(request, 'inc.html')