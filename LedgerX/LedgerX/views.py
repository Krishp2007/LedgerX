from django.shortcuts import render, redirect

def root_view(request):
    """
    Smart root:
    - If logged in → dashboard
    - Else → home page
    """
    if request.user.is_authenticated:
        return redirect('dashboard')  # Dashboard
    return render(request, 'public/home.html')


def about(request):
    return render(request, 'public/about.html')


def contact(request):
    return render(request, 'public/contact.html')
