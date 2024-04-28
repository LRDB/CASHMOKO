from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib import messages
from .models import Person
from .forms import CreateTransactionEntry
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

    # for k, v in m.items():
    #     if v["done"] == False:
    #         end = v["endBank"].upper()
    #         start = v["startBank"].upper()
    #         if v["type"] == "debit":
    #             banks[end] += v["amount"]
    #         elif v["type"] == "credit":
    #             banks[end] -= v["amount"]
    #         elif v["type"] == "banktransfer":
    #             banks[start] -= v["amount"]
    #             banks[end] += v["amount"]
    #         v["done"] = True

    for bank in banks:
        if bank in ["BDO", "BPI"]:
            accounts["Bank"] += banks[bank]
        elif bank == "Wallet".upper():
            accounts["Cash"] += banks[bank]
        elif bank in ["MAYA", "GCASH"]:
            accounts["E-Wallet"] += banks[bank]

    person.save()
    last_transactions = [v for k, v in list(m.items())[::-1] if k != "0"][:10]
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
    person = ls.person

    message = None

    if response.method == "POST":
        form = CreateTransactionEntry(ls, "dep_category", response.POST)
        moneytransactions = person.moneytransactions
        if form.is_valid():
            new_log = {
                "date": str(
                    datetime.datetime.now(TIMEZONE).strftime("%Y:%m:%d %H:%M:%S")
                ),
                "type": "debit",
                "category": form.cleaned_data["category"],
                "amount": form.cleaned_data["amount"],
                "startBank": "None",
                "endBank": form.cleaned_data["endBank"],
                "done": False,
            }
            transaction_id = len(moneytransactions)  # Use the length as a unique key
            moneytransactions[str(transaction_id)] = new_log
            person.save()

        m = person.moneytransactions
        banks = person.bankaccounts
        for k, v in m.items():
            end = v["endBank"].upper()
            if v["type"] == "debit" and v["done"] == False:
                banks[end] += v["amount"]
            v["done"] = True

        person.save()
        message = messages.success(response, "Transaction successful!")
    else:
        form = CreateTransactionEntry(ls, "dep_category")
    return render(
        response, "main/debit.html", {"form": form, "ls": ls, "message": message}
    )


@csrf_protect
@login_required
def Credit(response):
    ls = response.user
    person = ls.person

    message = None
    if response.method == "POST":
        form = CreateTransactionEntry(ls, "cred_category", response.POST)
        moneytransactions = person.moneytransactions
        if form.is_valid():
            new_log = {
                "date": str(
                    datetime.datetime.now(TIMEZONE).strftime("%Y:%m:%d %H:%M:%S")
                ),
                "type": "credit",
                "category": form.cleaned_data["category"],
                "amount": form.cleaned_data["amount"],
                "startBank": "None",
                "endBank": form.cleaned_data["endBank"],
                "done": False,
            }
            transaction_id = len(moneytransactions)  # Use the length as a unique key
            moneytransactions[str(transaction_id)] = new_log
            person.save()

        m = person.moneytransactions
        banks = person.bankaccounts
        for k, v in m.items():
            end = v["endBank"].upper()
            if v["type"] == "credit" and v["done"] == False:
                banks[end] -= v["amount"]
            v["done"] = True

        person.save()

        message = messages.success(response, "Transaction successful!")
    else:
        form = CreateTransactionEntry(ls, "cred_category")

    return render(
        response, "main/credit.html", {"form": form, "ls": ls, "message": message}
    )


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


@csrf_protect
@login_required
def profile(response):
    ls = response.user
    person = ls.person
    banks = ", ".join([key for key in person.bankaccounts.keys() if key != "NONE"])

    if response.method == "POST":
        if "inputFirstName" in response.POST:
            fname = response.POST["inputFirstName"]
            if fname:
                ls.first_name = fname
                ls.save()
        if "inputLastName" in response.POST:
            lname = response.POST["inputLastName"]
            if lname:
                ls.last_name = lname
                ls.save()
        if "dep_cat" in response.POST:
            dep_cat = response.POST["dep_cat"].title()
            if dep_cat:
                if dep_cat in person.dep_category:
                    del person.dep_category[dep_cat]  # Remove the category if it exists
                else:
                    person.dep_category[dep_cat] = dep_cat
                person.save()

        if "cred_cat" in response.POST:
            cred_cat = response.POST["cred_cat"].title()
            if cred_cat:
                if cred_cat in person.cred_category:
                    del person.cred_category[
                        cred_cat
                    ]  # Remove the category if it exists
                else:
                    person.cred_category[cred_cat] = cred_cat
                person.save()

        return redirect("profile")
    return render(
        response,
        "main/profile.html",
        {"ls": ls, "banks": banks},
    )
