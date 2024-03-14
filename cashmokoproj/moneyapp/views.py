from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from cashmokoproj import settings
import smtplib
from email.message import EmailMessage
import random


@csrf_protect
def home(request):
    if request.user.is_authenticated:
        return render(request, "moneyapp/mainpage.html")
    else:
        return render(request, "moneyapp/login.html")


def logout_user(request):
    logout(request)
    return redirect("home")


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
    if isinstance(request.user, AnonymousUser):
        name = "Guest"  # Or any default name you prefer
    else:
        fname = request.user.first_name
        lname = request.user.last_name
        name = f"{fname} {lname}"
    return render(request, "moneyapp/mainpage.html", {"name": name})


@csrf_protect
@login_required
def userprofile(request):
    fname = request.user.first_name
    lname = request.user.last_name
    name = f"{fname} {lname}"
    username = request.user.username
    email = request.user.email

    if request.method == "POST":
        new_name = request.POST["name"]
        if new_name == "":
            return redirect("userprofile")

        new_first, new_last = new_name.split(" ")

        user = request.user
        user.first_name = new_first
        user.last_name = new_last

        user.save()

        return redirect("userprofile")

    return render(
        request,
        "moneyapp/userprofile.html",
        {"name": name, "email": email, "username": username},
    )


@csrf_protect
@login_required
def userbalances(request):
    fname = request.user.first_name
    lname = request.user.last_name
    name = f"{fname} {lname}"
    # name = request.user.username
    return render(request, "moneyapp/userbalances.html", {"name": name})


@csrf_protect
@login_required
def useripon(request):
    fname = request.user.first_name
    lname = request.user.last_name
    name = f"{fname} {lname}"
    # name = request.user.username
    return render(request, "moneyapp/useripon.html", {"name": name})


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
