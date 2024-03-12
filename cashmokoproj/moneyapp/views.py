from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from cashmokoproj import settings
import smtplib
from email.message import EmailMessage
import random


@csrf_protect
# Create your views here.
def home(request):
    return render(request, "moneyapp/login.html")


@csrf_protect
def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if not username or not password:
            messages.error(
                request, "Username and password cannot be empty. Please try again!"
            )
            return redirect("home")

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("mainpage")
        else:
            messages.error(request, "Wrong username or password. Please try again!")
            return redirect("home")
    else:
        return redirect("home")


@csrf_protect
@login_required
def mainpage(request):
    username = request.user.username
    return render(request, "moneyapp/mainpage.html", {"name": username})


@csrf_protect
def userprofile(request):
    return render(request, "moneyapp/userprofile.html")


@csrf_protect
@login_required
def userbalances(request):
    username = request.user.username
    return render(request, "moneyapp/userbalances.html", {"name": username})


@csrf_protect
@login_required
def useripon(request):
    username = request.user.username
    return render(request, "moneyapp/useripon.html", {"name": username})


def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        ver = random.randint(10**5, 10**6 + 1)

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists. Try another username")
            return redirect("signup")

        if User.objects.filter(email=email):
            messages.error(request, "Email already exists. Try another email.")
            return redirect("signup")

        user = User.objects.create_user(username, email, password)
        user.pin = ver
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        messages.success(request, "Sign-up was successful")

        # EMAIL
        subject = "CASHMOKO: Cash Kita Verification Pin"
        message = f"Your pin is {user.pin}."

        email_msg = EmailMessage()
        email_msg["From"] = settings.EMAIL_HOST_USER
        email_msg["To"] = user.email
        email_msg["Subject"] = subject
        email_msg.set_content(message)

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            smtp.send_message(email_msg)
        return redirect("login")
    return render(request, "moneyapp/signup.html")
