from django.db import models as m
from django.contrib.auth.models import User


# Create your models here.
class Person(m.Model):
    user = m.OneToOneField(User, null=True, on_delete=m.CASCADE)
    first_name = m.CharField(max_length=200, default="NAME")
    last_name = m.CharField(max_length=200, default="NAME")
    email = m.EmailField(default="NAME@gmail.com")
