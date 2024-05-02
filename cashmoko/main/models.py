from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_pin = models.IntegerField(default=0)
    moneytransactions = models.JSONField(default=dict)
    bankaccounts = models.JSONField(default=dict)
    banks = models.JSONField(default=dict)
    verified = models.BooleanField(default=False)
    new_login = models.BooleanField(default=True)
    quote = models.TextField(default="")
    currency = models.JSONField(default=dict)
    dep_category = models.JSONField(default=dict)
    cred_category = models.JSONField(default=dict)
    # adj_category = models.JSONField(default=dict)
