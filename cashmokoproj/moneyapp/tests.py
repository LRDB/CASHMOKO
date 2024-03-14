# from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth.models import User


class LoginTestCase(TestCase):

    def test_valid_login(self):
        client = Client()
        response = client.post(
            "/login/", {"username": "papapips", "password": "joshua08"}
        )
        self.assertEqual(
            response.status_code, 302
        )  # Assuming successful login redirects to mainpage

    def test_empty_username_or_password(self):
        client = Client()
        response = client.post("/login/", {"username": "", "password": ""})
        self.assertEqual(
            response.status_code, 302
        )  # Assuming empty fields redirect to home
        self.assertRedirects(response, "/home/")

    def test_invalid_login(self):
        client = Client()
        response = client.post(
            "/login/", {"username": "invaliduser", "password": "invalidpassword"}
        )
        self.assertEqual(
            response.status_code, 302
        )  # Assuming invalid login redirects to home
        self.assertRedirects(response, "/home/")
        self.assertContains(response, "Wrong username or password. Please try again!")
