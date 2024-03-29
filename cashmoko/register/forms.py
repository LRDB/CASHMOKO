from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CreatePerson(UserCreationForm):
    firstname = forms.CharField(label="First Name", max_length=200)
    lastname = forms.CharField(label="Last Name", max_length=200)
    email = forms.EmailField(max_length=300)

    class Meta:
        model = User
        fields = [
            "firstname",
            "lastname",
            "username",
            "email",
            "password1",
            "password2",
        ]


class VerifyPerson(forms.Form):
    email_pin = forms.CharField(label="Verification Pin", max_length=6)
