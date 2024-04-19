from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from main.forms import CreateTransactionEntry
from django.urls import path
from django.contrib.auth.models import User
from django.test import Client
from main.models import Person
import random
import datetime
import pytz


TIMEZONE = pytz.timezone("Asia/Manila")
INITIAL_BALANCE = round(0.00, 2)

class Sprint3TestBasis(TestCase):
        
    def setUp(self):        
        self.url_login = reverse("home")
        self.url_user_balances = reverse("user_balances")
        self.url_debit = reverse("Debit")
        self.url_credit = reverse("Credit")
        self.url_bank_transfer = reverse("Bank Transfer")
        self.url_ipon_challenge = reverse("iponchallenge")
        self.url_manual_edit = reverse("Manual Edit")

        user = User.objects.create_user(username="hashimoto",email="real@email.com",password="kanna")
        user.Person = Person.objects.create(
            user=user,
            email_pin=123456,
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
            },
            bankaccounts = {
                "BDO": INITIAL_BALANCE,
                "BPI": INITIAL_BALANCE,
                "MAYA": INITIAL_BALANCE,
                "GCASH": INITIAL_BALANCE,
                "WALLET": INITIAL_BALANCE,
                "IPON": INITIAL_BALANCE,
                "NONE": INITIAL_BALANCE,
            },
            verified=True,
        )
        user.save()
        
        self.client = Client()
        self.client.login(username="hashimoto",password="kanna")

        return super().setUp()
        
class URLAccessTests(Sprint3TestBasis):
        
    def test_url_user_balances_exists(self):
        response = self.client.get(self.url_user_balances, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/userbalances.html")
    
    def test_url_debit_exists(self):
        response = self.client.get(self.url_debit, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/debit.html")

    def test_url_credit_exists(self):
        response = self.client.get(self.url_credit, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/credit.html")

    def test_url_bank_transfer_exists(self):
        response = self.client.get(self.url_bank_transfer, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/bank_transfer.html")

    def test_url_ipon_challenge_exists(self):
        response = self.client.get(self.url_ipon_challenge, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/iponchallenge.html")

    def test_url_manual_edit_exists(self):
        response = self.client.get(self.url_manual_edit, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/manual_edit.html")
        
class TransactionFormTest(Sprint3TestBasis):
    
    def test_forms(self):
        form_data = {"category":"hashimoto kanna","amount":1000000000,"startBank":"None","endBank":"Maya"}
        form = CreateTransactionEntry(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_forms_incorrect_data(self):
        form_data = {"category":12031023,"amount":"MONEY","startBank":"NOT A REAL CHOICE","endBank":"Gcshdsfsdf"}
        form = CreateTransactionEntry(data=form_data)
        self.assertFalse(form.is_valid())