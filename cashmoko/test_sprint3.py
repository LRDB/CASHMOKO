from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from main.forms import (
    CreateTransactionEntry,
    CreateIponTransactionEntry,
    BankTransactionEntry,
    BankTransferTransactionEntry,
)
from django.urls import path
from django.contrib.auth.models import User
from django.test import Client
from main.models import Person
import random
import datetime
import pytz
import os
from django.http import HttpResponse


TIMEZONE = pytz.timezone("Asia/Manila")
INITIAL_BALANCE = round(0.00, 2)


class Sprint3TestBasis(TestCase):

    def setUp(self):
        self.url_bank_transfer = reverse("Bank Transfer")
        self.url_ipon_challenge = reverse("iponchallenge")
        self.url_manual_edit = reverse("Adjustment")

        self.user = User.objects.create_user(
            username="hashimoto", email="real@email.com", password="kanna"
        )
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
        }
        self.user.Person = Person.objects.create(
            user=self.user,
            email_pin=123456,
            moneytransactions={
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
            },
            bankaccounts={
                "BDO": INITIAL_BALANCE,
                "BPI": INITIAL_BALANCE,
                "MAYA": INITIAL_BALANCE,
                "GCASH": INITIAL_BALANCE,
                "WALLET": INITIAL_BALANCE,
                "IPON": INITIAL_BALANCE,
                "NONE": INITIAL_BALANCE,
            },
            banks={
                "Gcash": "Gcash",
                "BPI": "BPI",
                "BDO": "BDO",
                "Maya": "Maya",
                "Wallet": "Wallet",
                "Ipon": "Ipon",
            },
            dep_category=categories["deposit"],
            cred_category=categories["credit"],
            verified=True,
        )
        self.user.save()

        self.client = Client()
        self.client.login(username="hashimoto", password="kanna")

        return super().setUp()


class URLAccessTests(Sprint3TestBasis):
    def test_url_ipon_challenge_exists(self):
        response = self.client.get(self.url_ipon_challenge, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/iponchallenge.html")

    def test_url_manual_edit_exists(self):
        response = self.client.get(self.url_manual_edit, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/manual_edit.html")


class TransactionFormTest(Sprint3TestBasis):

    def test_CreateIponChallenge(self):
        form_data = {"amount": 69}
        form = CreateIponTransactionEntry(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_CreateIponChallengeERROR(self):
        form_data = {"amount": "OneBajillion"}
        form = CreateIponTransactionEntry(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())

    def test_BankTransaction(self):
        form_data = {"amount": 69, "endBank": "Maya"}
        form = BankTransactionEntry(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_BankTransactionERROR_endbank404(self):
        form_data = {"amount": 69, "endBank": "MAGICBANK"}
        form = BankTransactionEntry(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())

    def test_CreateTransactionEntry_Dr(self):
        form_data = {"amount": 69, "endBank": "Maya", "category": "Allowance"}
        form = CreateTransactionEntry(
            user=self.user, cat="dep_category", data=form_data
        )
        self.assertTrue(form.is_valid())

    def test_CreateTransactionEntry_DrERROR(self):
        form_data = {"amount": 69, "endBank": "Maya", "category": "MAGICAL LOTTERY"}
        form = CreateTransactionEntry(
            user=self.user, cat="dep_category", data=form_data
        )
        self.assertFalse(form.is_valid())

    def test_CreateTransactionEntry_Cr(self):
        form_data = {"amount": 69, "endBank": "Maya", "category": "Food"}
        form = CreateTransactionEntry(
            user=self.user, cat="cred_category", data=form_data
        )
        self.assertTrue(form.is_valid())

    def test_CreateTransactionEntry_CrERROR(self):
        form_data = {
            "amount": 69,
            "endBank": "Maya",
            "category": "Hardcore Illegal Drugs",
        }
        form = CreateTransactionEntry(
            user=self.user, cat="cred_category", data=form_data
        )
        self.assertFalse(form.is_valid())

    def test_BankTransfTransactEntry(self):
        form_data = {"amount": 69, "startBank": "Gcash", "endBank": "Maya"}
        form = BankTransferTransactionEntry(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_BankTransfTransactEntry_ERROR_start404(self):
        form_data = {"amount": 69, "startBank": "MYSTERY MONEY", "endBank": "Maya"}
        form = BankTransferTransactionEntry(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())

    def test_BankTransfTransactEntry_ERROR_end404(self):
        form_data = {"amount": 69, "startBank": "Gcash", "endBank": "MOYA MONEY"}
        form = BankTransferTransactionEntry(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
