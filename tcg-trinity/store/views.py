from django.shortcuts import render
from .models import Product, Event
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        full_message = f"Message from {name} ({email}):\n\n{message}"

        # Send the email (make sure EMAIL settings are configured)
        send_mail(
            subject="New Contact Form Submission - TCG Trinity",
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
        )

        messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
    
    return render(request, 'contact.html')


def home(request):
    products = Product.objects.all()[:6]  # show 6 featured products
    return render(request, 'home.html', {'products': products})


from urllib.parse import quote

def events(request):
    events = Event.objects.all().order_by('start_time')
    return render(request, 'events.html', {'events': events})


def product_list(request):
    products = Product.objects.all()

    # Search
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    # Sort
    sort = request.GET.get('sort')
    if sort == 'price':
        products = products.order_by('price')
    elif sort == '-price':
        products = products.order_by('-price')

    return render(request, 'product_list.html', {'products': products})

def events_view(request):
    events = Event.objects.all()  # or filter upcoming
    return render(request, 'events.html', {'events': events})

from django.shortcuts import render

def open_play(request):
    return render(request, 'open_play.html')
