from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib import messages
from .models import Person
from register.forms import CreatePerson
import random
import datetime
import smtplib
from email.message import EmailMessage
from cashmoko import settings


def emailMessage(user, p):
    subject = "CASHMOKO: Cash Kita Verification Pin"
    message = f"Your pin is {p.email_pin}."

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


def logout_user(request):
    logout(request)
    return redirect("home")


@csrf_protect
def home(response):
    return redirect("login")


@csrf_protect
@login_required
def userpage(response):
    ls = response.user
    if ls.person.verified == False:
        p = ls.person
        emailMessage(ls, p)
        return redirect("verifyEmail")

    ## Guide for making new transactions
    # person = ls.person
    # moneytransactions = person.moneytransactions
    # new_log = {
    #     "date": str(datetime.datetime.now()),
    #     "type": "debit",
    #     "category": "allowance",
    #     "amount": 1000,
    #     "startBank": "BDO",
    #     "endBank": "wallet",
    # }
    # transaction_id = len(moneytransactions)  # Use the length as a unique key
    # moneytransactions[str(transaction_id)] = new_log
    # person.save()
    return render(response, "main/userpage.html", {"ls": ls})
