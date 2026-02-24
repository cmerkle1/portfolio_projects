from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request, "home.html")

def about(request):
    return render(request, "about.html")

def events(request):
    return render(request, "events.html")

def menu(request):
    return render(request, "menu.html")

def newsletter_signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        print("New email signup:", email)
        messages.success(request, "Thanks for signing up!")
        return redirect("home")
