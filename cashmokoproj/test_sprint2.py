from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login


class Sprint2TestBasis(TestCase):

    def setUp(self):
        self.existing_user = {"username": "joshua", "password": "joshua"}
        self.new_user = {
            "username": "nina",
            "password": "sapitula",
            "email": "nina@sapitula.com",
            "first_name": "Nina",
            "last_name": "Sapitula",
        }
        self.new_user_login_correct = {"username": "nina", "password": "sapitula"}
        self.new_user_login_wrong = {"username": "nina", "password": "spatula"}
        self.new_user_same_username = {
            "username": "nina",
            "password": "sapitula",
            "email": "nina12345@sapitula.com",
            "first_name": "Nina",
            "last_name": "Sapitula",
        }
        self.new_user_same_email = {
            "username": "nina12345",
            "password": "sapitula",
            "email": "nina@sapitula.com",
            "first_name": "Nina",
            "last_name": "Sapitula",
        }
        self.new_user_empty = {
            "username": "",
            "password": "",
            "email": "",
            "first_name": "",
            "last_name": "",
        }
        self.login_url = reverse("home")
        self.signup_url = reverse("signup")
        self.mainpage_url = reverse("mainpage")
        self.userprofile_url = reverse("userprofile")
        self.userbalances_url = reverse("userbalances")
        self.useripon_url = reverse("useripon")

        return super().setUp()


class UnloggedAccessTests(Sprint2TestBasis):
    # Tests URL accesses by users that are not logged in

    def test_login_url_exists(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "moneyapp/login.html")

    def test_mainpage_inaccessible_without_login(self):
        response = self.client.get(self.mainpage_url)
        self.assertEqual(response.status_code, 302)

    def test_userprofile_inaccessible_without_login(self):
        response = self.client.get(self.userprofile_url)
        self.assertEqual(response.status_code, 302)

    def test_userbalances_inaccessible_without_login(self):
        response = self.client.get(self.userbalances_url)
        self.assertEqual(response.status_code, 302)

    def test_useripon_inaccessible_without_login(self):
        response = self.client.get(self.useripon_url)
        self.assertEqual(response.status_code, 302)

    def test_signup_url_exists(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "moneyapp/signup.html")

    def test_signup_possible(self):
        response = self.client.post(self.signup_url, self.new_user, format="text/html")
        self.assertEqual(response.status_code, 302)


class RegistrationTests(Sprint2TestBasis):
    # User can register a new account
    def test_signup_username_already_taken(self):
        response = self.client.post(
            self.signup_url, self.new_user_same_username, format="text/html"
        )
        self.assertEqual(response.status_code, 302)

    def test_signup_email_already_taken(self):
        response = self.client.post(
            self.signup_url, self.new_user_same_email, format="text/html"
        )
        self.assertEqual(response.status_code, 302)

    def test_can_signup(self):
        response = self.client.post(self.signup_url, self.new_user, format="text/html")
        self.assertEqual(response.status_code, 302)

    def test_login_with_new_account(self):
        self.client.post(self.signup_url, self.new_user_same_email, format="text/html")
        response = self.client.post(
            self.login_url, self.new_user_login_correct, format="text/html"
        )
        self.assertEqual(response.status_code, 200)

    def test_logged_user_can_access_homepage(self):
        self.client.post(self.signup_url, self.new_user_same_email, format="text/html")
        response = self.client.post(
            self.login_url, self.new_user_login_correct, format="text/html"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "moneyapp/mainpage.html")

    # def test_signup_you_need_to_input_complete_info(self):
    #    response=self.client.post(self.signup_url,self.new_user_empty,format='text/html')
    #    self.assertEqual(response.status_code, 401)
