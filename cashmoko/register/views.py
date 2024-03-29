from django.shortcuts import render, redirect
from .forms import CreatePerson, VerifyPerson
from django.contrib.auth.forms import UserCreationForm
from main.models import Person
from django.contrib import messages
import random
import datetime
import pytz

TIMEZONE = pytz.timezone("Asia/Manila")


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
                "BDO": 0,
                "BPI": 0,
                "MAYA": 0,
                "GCASH": 0,
                "WALLET": 0,
                "IPON": 0,
                "NONE": 0,
            }
            user = form.save(commit=False)
            user.first_name = form.cleaned_data["firstname"]
            user.last_name = form.cleaned_data["lastname"]
            user.save()
            Person.objects.create(
                user=user,
                email_pin=pin,
                moneytransactions=moneytransactions,
                bankaccounts=bankaccounts,
                verified=False,
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
