from django.shortcuts import render, redirect
from .forms import CreatePerson, VerifyPerson
from django.contrib.auth.forms import UserCreationForm
from main.models import Person
from django.contrib import messages
import random
import datetime
import pytz

TIMEZONE = pytz.timezone("Asia/Manila")
INITIAL_BALANCE = round(0.00, 2)
WALLET = "WALLET"
EWALLET = "E-WALLET"
BANK = "BANK"


# Create your views here.
def register(response):
    if response.method == "POST":
        form = CreatePerson(response.POST)
        if form.is_valid():
            pin = random.randint(10**5, 10**6 + 1)
            moneytransactions = {
                0: {
                    "date": str(
                        datetime.datetime.now(TIMEZONE).strftime("%Y:%m:%d %H:%M:%S")
                    ),
                    "type": "None",
                    "category": "None",
                    "amount": 0,
                    "startBank": "None",
                    "endBank": "None",
                    "done": False,
                },
            }

            bankaccounts = {
                "BDO": [INITIAL_BALANCE, BANK],
                "BPI": [INITIAL_BALANCE, BANK],
                "MAYA": [INITIAL_BALANCE, EWALLET],
                "GCASH": [INITIAL_BALANCE, EWALLET],
                "WALLET": [INITIAL_BALANCE, WALLET],
                "IPON": [INITIAL_BALANCE, None],
                "NONE": [INITIAL_BALANCE, None],
            }

            banks = {
                "Gcash": "Gcash",
                "BPI": "BPI",
                "BDO": "BDO",
                "Maya": "Maya",
                "Wallet": "Wallet",
                "Ipon": "Ipon",
            }

            categories = {
                "deposit": {
                    "Allowance": "Allowance",
                    "Scholarship": "Scholarship",
                    "Donation": "Donation",
                    "Salary": "Salary",
                },
                "credit": {
                    "Food": "Food",
                    "Transportation": "Transportation",
                    "Rent": "Rent",
                    "Utilities": "Utilities",
                    "Clothes": "Clothes",
                    "Medicine": "Medicine",
                    "Grocery": "Grocery",
                    "Insurance": "Insurance",
                    "Lifestyle": "Lifestyle",
                },
                # "adjustments": {
                #     "Adjustments": "Adjustments",
                # },
            }

            feedback = {"0": {"title": "", "content": "", "resolved": ""}}
            user = form.save(commit=False)
            user.first_name = form.cleaned_data["firstname"]
            user.last_name = form.cleaned_data["lastname"]
            user.save()
            Person.objects.create(
                user=user,
                email_pin=pin,
                moneytransactions=moneytransactions,
                bankaccounts=bankaccounts,
                banks=banks,
                verified=False,
                dep_category=categories["deposit"],
                cred_category=categories["credit"],
                feedback=feedback,
                # adj_category=categories["adjustments"],
            )
            messages.success(response, "Sign-up was successful")
            return redirect("login")
    else:
        form = CreatePerson()
    return render(response, "register/register.html", {"form": form})


def verifyEmail(response):
    user = response.user
    p = user.person
    if response.method == "POST":
        form = VerifyPerson(response.POST)
        if form.is_valid():
            key = p.email_pin
            if str(key) == form.cleaned_data["email_pin"]:
                p.verified = True
                p.save()
                return redirect("userpage")
            else:
                messages.error(response, "Incorrect verification pin.")
                return redirect("verifyEmail")
    else:
        form = VerifyPerson()
    return render(response, "register/verify.html", {"form": form})
