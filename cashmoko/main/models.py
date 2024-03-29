from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_pin = models.IntegerField(default=0)
    moneytransactions = models.JSONField(default=dict)
    bankaccounts = models.JSONField(default=dict)
    verified = models.BooleanField(default=False)
