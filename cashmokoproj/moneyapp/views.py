from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request, "moneyapp/login.html")

def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = User.objects.create_user(username, password)
        user.save()

        messages.success(request, "Login Successful")
        
        return redirect("main")
def mainpage(request):
    pass