from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib import messages
from .models import Person
from .forms import (
    CreateTransactionEntry,
    CreateIponTransactionEntry,
    BankTransactionEntry,
    BankTransferTransactionEntry,
)
from register.forms import CreatePerson
from .quotes import quote
from .currency import get_currency
import random
import datetime
import pytz
import smtplib
from email.message import EmailMessage
from cashmoko import settings

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from pandas.plotting import table

TIMEZONE = pytz.timezone("Asia/Manila")


def show_balance(response):
    accounts = {"Cash": 0.0, "E-Wallet": 0.0, "Bank": 0.0}
    transaction_types = [
        "Debit",
        "Credit",
        "Bank Transfer",
        "Adjustment",
        "Transactions",
    ]

    ls = response.user
    person = ls.person
    m = person.moneytransactions
    banks = person.bankaccounts

    for bank in banks:
        if banks[bank][1] == "BANK":
            accounts["Bank"] += banks[bank][0]
        elif banks[bank][1] == "WALLET":
            accounts["Cash"] += banks[bank][0]
        elif banks[bank][1] == "E-WALLET":
            accounts["E-Wallet"] += banks[bank][0]
    return accounts, transaction_types


def emailMessage(user, p, subject, message):
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
    ls = response.user
    if ls.person.verified == False:
        p = ls.person
        emailMessage(
            ls, p, "CASHMOKO: Cash Kita Verification Pin", f"Your pin is {p.email_pin}."
        )
        return redirect("verifyEmail")

    person = ls.person
    if person.new_login:
        person.new_login = False
        person.quote = quote()["quote"]
        person.currency = get_currency()

    m = person.moneytransactions
    banks = person.bankaccounts

    accounts, _ = show_balance(response)

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
    ls = response.user
    person = ls.person
    m = person.moneytransactions
    banks = person.bankaccounts
    accounts, transaction_types = show_balance(response)
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
    person = ls.person

    message = None

    if response.method == "POST":
        form = CreateIponTransactionEntry(ls, response.POST)
        moneytransactions = person.moneytransactions
        if form.is_valid():
            new_log = {
                "date": str(
                    datetime.datetime.now(TIMEZONE).strftime("%Y:%m:%d %H:%M:%S")
                ),
                "type": "debit",
                "category": "Ipon",
                "amount": form.cleaned_data["amount"],
                "startBank": "None",
                "endBank": "Ipon",
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
                banks[end][0] += v["amount"]
            v["done"] = True

        person.save()
        message = messages.success(response, "Ipon successful!")
    else:
        form = CreateIponTransactionEntry(ls)
    return render(
        response,
        "main/iponchallenge.html",
        {"form": form, "ls": ls, "message": message},
    )


@csrf_protect
@login_required
def Debit(response):
    ls = response.user
    person = ls.person

    accounts, _ = show_balance(response)
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
                banks[end][0] += v["amount"]
            v["done"] = True

        person.save()
        message = messages.success(response, "Transaction successful!")
    else:
        form = CreateTransactionEntry(ls, "dep_category")
    return render(
        response, "main/debit.html", {"form": form, "ls": ls, "message": message, "accounts": accounts}
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
                banks[end][0] -= v["amount"]
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
def Adjustment(response):
    ls = response.user
    person = ls.person

    message = None

    if response.method == "POST":
        form = BankTransactionEntry(ls, response.POST)
        moneytransactions = person.moneytransactions
        if form.is_valid():
            new_log = {
                "date": str(
                    datetime.datetime.now(TIMEZONE).strftime("%Y:%m:%d %H:%M:%S")
                ),
                "type": "Adjustment",
                "category": "Adjustment",
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
            if v["type"] == "Adjustment" and v["done"] == False:
                banks[end][0] = v["amount"]
            v["done"] = True

        person.save()
        message = messages.success(response, "Editing successful!")
    else:
        form = BankTransactionEntry(ls)
    return render(
        response, "main/manual_edit.html", {"form": form, "ls": ls, "message": message}
    )


@csrf_protect
@login_required
def Bank_Transfer(response):
    ls = response.user
    person = ls.person

    message = None
    if response.method == "POST":
        form = BankTransferTransactionEntry(ls, response.POST)
        moneytransactions = person.moneytransactions
        if form.is_valid():

            new_log_credit = {
                "date": str(
                    datetime.datetime.now(TIMEZONE).strftime("%Y:%m:%d %H:%M:%S")
                ),
                "type": "credit",
                "category": "Bank Transfer",
                "amount": form.cleaned_data["amount"],
                "startBank": "None",
                "endBank": form.cleaned_data["startBank"],
                "done": False,
            }

            transaction_id = len(moneytransactions)  # Use the length as a unique key
            moneytransactions[str(transaction_id)] = new_log_credit
            person.save()

            new_log_debit = {
                "date": str(
                    datetime.datetime.now(TIMEZONE).strftime("%Y:%m:%d %H:%M:%S")
                ),
                "type": "debit",
                "category": "Bank Transfer",
                "amount": form.cleaned_data["amount"],
                "startBank": "None",
                "endBank": form.cleaned_data["endBank"],
                "done": False,
            }

            transaction_id = len(moneytransactions)  # Use the length as a unique key
            moneytransactions[str(transaction_id)] = new_log_debit
            person.save()

        m = person.moneytransactions
        banks = person.bankaccounts
        for k, v in m.items():
            end = v["endBank"].upper()
            if v["type"] == "credit" and v["done"] == False:
                banks[end][0] -= v["amount"]
            if v["type"] == "debit" and v["done"] == False:
                banks[end][0] += v["amount"]
            v["done"] = True

        person.save()

        message = messages.success(response, "Transaction successful!")
    else:
        form = BankTransferTransactionEntry(ls)

    return render(
        response,
        "main/bank_transfer.html",
        {"form": form, "ls": ls, "message": message},
    )


@csrf_protect
@login_required
def Transactions(response):
    ls = response.user
    person = ls.person
    m = person.moneytransactions
    banks = person.bankaccounts
    last_transactions = [v for k, v in list(m.items())[::-1] if k != "0"]

    # Get filter values from GET response
    if response.method == "POST":
        category = response.POST.get("category")
        transaction_type = response.POST.get("type")

        # Apply filters if they are not None
        if category:
            last_transactions = [
                transaction
                for transaction in last_transactions
                if transaction["category"] == category
            ]
        if transaction_type:
            last_transactions = [
                transaction
                for transaction in last_transactions
                if transaction["type"] == transaction_type
            ]
        response.session["last_transactions"] = last_transactions
        return redirect("Transactions")

    last_transactions = response.session.get("last_transactions", last_transactions)

    return render(
        response,
        "main/transactions.html",
        {
            "ls": ls,
            "categories": list(person.dep_category.keys())
            + list(person.cred_category.keys())
            + ["Ipon", "Bank Transfer", "Others"],
            "types": ["debit", "credit", "Adjustment"],
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

        if "bank" in response.POST:
            bank = response.POST["bank"].title()
            if bank:
                if bank in person.banks:
                    del person.banks[bank]  # Remove the bank if it exists
                    bank = bank.upper()
                    del person.bankaccounts[
                        bank
                    ]  # Remove the bank account if it exists
                else:
                    bank_type = response.POST["bank_type"]
                    if bank_type == "OTHERS":
                        bank_type = ""
                    person.banks[bank] = bank  # Create the bank if it doesn't exist
                    person.bankaccounts[bank.upper()] = (
                        0.0,
                        bank_type,  # Create the bank account if it doesn't exist
                    )

                person.save()
        return redirect("profile")
    return render(
        response,
        "main/profile.html",
        {"ls": ls, "banks": banks},
    )


@csrf_protect
@login_required
def feedback(response):
    ls = response.user
    person = ls.person
    transaction_id = len(person.feedback.keys())
    feed = [v for k, v in list(person.feedback.items())[::-1]]

    if response.method == "POST":
        if "concern" in response.POST:
            title = response.POST["subject"]
            feedback = response.POST["concern"]
            resolved = str(False)
            transaction_id = len(person.feedback.keys())
            if feedback:
                transaction = {
                    "title": title,
                    "content": feedback,
                    "resolved": resolved,
                    "date": str(
                        datetime.datetime.now(TIMEZONE).strftime("%Y:%m:%d %H:%M:%S")
                    ),
                }
                person.feedback[str(transaction_id)] = transaction
                person.save()

                messageToUser = f'We received your feedback.\nYour concern is: "{person.feedback[str(transaction_id)]["content"]}"\n\nWe will get back to you soon.\n\nRegards,\n\nCASHMOKO: Cash Kita Team'

                emailMessage(ls, person, "CASHMOKO: Feedback", messageToUser)
            return redirect("feedback")
    return render(response, "main/feedback.html", {"feedback": feed})

@csrf_protect
@login_required
def emailsummary(response):
    ls = response.user
    person = ls.person
    m = person.moneytransactions
    
    plt.figure(0)
    dep_labels = list(person.dep_category.keys())
    dep_amounts = [0] * len(dep_labels)
    
    for i in range(0, len(dep_labels)):
        for k, v in m.items():
            if (v["category"] == dep_labels[i]):
                dep_amounts[i] = dep_amounts[i] + v["amount"]

    formatted_dep_labels = []
    formatted_dep_amounts = []
    
    for i in range(0, len(dep_labels)):
        if (dep_amounts[i] != 0):
            formatted_dep_labels.append(dep_labels[i])
            formatted_dep_amounts.append(dep_amounts[i])
    
    plt.pie(formatted_dep_amounts, labels=formatted_dep_labels)
    
    cred_labels = list(person.cred_category.keys())
    cred_amounts = [0] * len(cred_labels)
    
    plt.figure(1)
    for i in range(0, len(cred_labels)):
        for k, v in m.items():
            if (v["category"] == cred_labels[i]):
                cred_amounts[i] = cred_amounts[i] + v["amount"]
    
    formatted_cred_labels = []
    formatted_cred_amounts = []
    
    for i in range(0, len(cred_labels)):
        if (cred_amounts[i] != 0):
            formatted_cred_labels.append(cred_labels[i])
            formatted_cred_amounts.append(cred_amounts[i])

    plt.pie(formatted_cred_amounts, labels=formatted_cred_labels)
    
    #Ugh
    accounts = {"Cash": 0.0, "E-Wallet": 0.0, "Bank": 0.0}
    banks = person.bankaccounts

    for bank in banks:
        if banks[bank][1] == "BANK":
            accounts["Bank"] += banks[bank][0]
        elif banks[bank][1] == "WALLET":
            accounts["Cash"] += banks[bank][0]
        elif banks[bank][1] == "E-WALLET":
            accounts["E-Wallet"] += banks[bank][0]
    
        
    plt.figure(2)
    #UGH!!!
    last_transactions = [v for k, v in list(m.items())[::-1] if k != "0"]
    
    some_transactions = []
    
    for i in range(0,5):
        some_transactions.append(last_transactions[i])

    df = pd.json_normalize(some_transactions)
    
    df = df.drop("startBank",axis=1)
    df = df.drop("endBank",axis=1)
    df = df.drop("done",axis=1)
    
    ax = plt.subplot(111, frame_on=False)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    
    table(ax,df,loc='center')
    
    save_multi_image("summary.pdf")

    messageToUser = f'This is your summary for: {datetime.datetime.now(TIMEZONE).strftime("%Y:%m:%d %H:%M:%S")}\nYour Account Balances:\nBANK: ₱{accounts["Bank"]}\nWALLET: ₱{accounts["Cash"]}\nE-WALLET: ₱{accounts["E-Wallet"]}\n'
    emailMessage(ls, person, "CASHMOKO: Summary", messageToUser, file="summary.pdf")
    
    return render(
        response,
        "main/emailsummary.html",
    )
   
def save_multi_image(filename):
    pp = PdfPages(filename)
    fig_nums = plt.get_fignums()
    figs = [plt.figure(n) for n in fig_nums]
    for fig in figs:
        fig.savefig(pp, format='pdf')
    pp.close()