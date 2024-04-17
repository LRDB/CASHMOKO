from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib import messages
from .models import Person
from register.forms import CreatePerson
from .quotes import quote
from .currency import get_currency
import random
import datetime
import pytz
import smtplib
from email.message import EmailMessage
from cashmoko import settings

TIMEZONE = pytz.timezone("Asia/Manila")


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


def logout_user(response):
    ls = response.user
    person = ls.person
    person.new_login = True
    person.save()
    logout(response)
    return redirect("home")


@csrf_protect
def home(response):
    return redirect("login")


@csrf_protect
@login_required
def userpage(response):
    accounts = {"Cash": 0.0, "E-Wallet": 0.0, "Bank": 0.0}

    ls = response.user
    if ls.person.verified == False:
        p = ls.person
        emailMessage(ls, p)
        return redirect("verifyEmail")

    person = ls.person
    if person.new_login:
        person.new_login = False
        person.quote = quote()["quote"]
        person.currency = get_currency()

    m = person.moneytransactions
    banks = person.bankaccounts

    ## Guide for making new transactions
    # moneytransactions = person.moneytransactions
    # new_log = {
    #     "date": str(datetime.datetime.now(TIMEZONE).strftime("%Y:%m:%d %H:%M:%S")),
    #     "type": "credit",
    #     "category": "KPOP Album",
    #     "amount": 483,
    #     "startBank": "None",
    #     "endBank": "Wallet",
    #     "done": False,
    # }
    # transaction_id = len(moneytransactions)  # Use the length as a unique key
    # moneytransactions[str(transaction_id)] = new_log

    for k, v in m.items():
        if v["done"] == False:
            end = v["endBank"].upper()
            start = v["startBank"].upper()
            if v["type"] == "debit":
                banks[end] += v["amount"]
            elif v["type"] == "credit":
                banks[end] -= v["amount"]
            elif v["type"] == "banktransfer":
                banks[start] -= v["amount"]
                banks[end] += v["amount"]
            v["done"] = True

    for bank in banks:
        if bank in ["BDO", "BPI"]:
            accounts["Bank"] += banks[bank]
        elif bank == "Wallet".upper():
            accounts["Cash"] += banks[bank]
        elif bank in ["MAYA", "GCASH"]:
            accounts["E-Wallet"] += banks[bank]

    person.save()
    last_transactions = [v for k, v in list(m.items())[::-1] if k != "0"][:8]
    q = person.quote
    currencies = person.currency
    return render(
        response,
        "main/userpage.html",
        {
            "ls": ls,
            "last_transactions": last_transactions,
            "q": q,
            "currencies": currencies,
            "accounts": accounts,
        },
    )


@csrf_protect
@login_required
def user_balances(response):
    accounts = {"Cash": 0.0, "E-Wallet": 0.0, "Bank": 0.0}
    transaction_types = [
        "Debit",
        "Credit",
        "Bank Transfer",
        "Manual Edit",
        "Transactions",
    ]

    ls = response.user
    person = ls.person
    m = person.moneytransactions
    banks = person.bankaccounts

    for bank in banks:
        if bank in ["BDO", "BPI"]:
            accounts["Bank"] += banks[bank]
        elif bank == "Wallet".upper():
            accounts["Cash"] += banks[bank]
        elif bank in ["MAYA", "GCASH"]:
            accounts["E-Wallet"] += banks[bank]

    return render(
        response,
        "main/userbalances.html",
        {
            "ls": ls,
            "transaction_types": transaction_types,
            "accounts": accounts,
        },
    )


@csrf_protect
@login_required
def iponchallenge(response):
    ls = response.user
    return render(response, "main/iponchallenge.html", {"ls": ls})


@csrf_protect
@login_required
def Debit(response):
    ls = response.user
    return render(response, "main/debit.html", {"ls": ls})


@csrf_protect
@login_required
def Credit(response):
    ls = response.user
    return render(response, "main/credit.html", {"ls": ls})


@csrf_protect
@login_required
def Manual_Edit(response):
    ls = response.user
    return render(response, "main/manual_edit.html", {"ls": ls})


@csrf_protect
@login_required
def Bank_Transfer(response):
    ls = response.user
    return render(response, "main/bank_transfer.html", {"ls": ls})


@csrf_protect
@login_required
def Transactions(response):
    ls = response.user
    person = ls.person
    m = person.moneytransactions
    banks = person.bankaccounts
    last_transactions = [v for k, v in list(m.items())[::-1] if k != "0"]
    return render(
        response,
        "main/transactions.html",
        {
            "ls": ls,
            "last_transactions": last_transactions,
        },
    )
