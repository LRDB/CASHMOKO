from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

@csrf_protect
# Create your views here.
def home(request):
    return render(request, "moneyapp/login.html")

@csrf_protect
def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, "moneyapp/mainpage.html", {"name" : username})
        else:
            messages.success(request, "Wrong username or password. Please try again!")
            return redirect("home")
    else:
        return render(request, "moneyapp/login.html")
    
# def signup(request):
#     if request.method == "POST":
#         username = request.POST["username"]
#         password = request.POST["password"]

#         user = User.objects.create_user(username, password)
#         user.save()

#         messages.success(request, "Login Successful")
        
#         return redirect("login")

@csrf_protect
def mainpage(request):
    return render(request, 'moneyapp/mainpage.html')