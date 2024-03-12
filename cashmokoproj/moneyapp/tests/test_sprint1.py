from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login

# Create your tests here.
class Sprint1Test(TestCase):

    def setUp(self):
        self.user_correct={
            'username':'papapips',
            'password':'joshua08'
        }
        self.user_empty={
            'username':'',
            'password':''
        }
        self.user_wrong={
            'username':'asdfghjkl',
            'password':'qwertyuiop'
        }
        self.login_url=reverse('home')
        self.homepage_url=reverse('mainpage')
        self.userprofile_url=reverse('userprofile')
        self.userbalances_url=reverse('userbalances')
        self.useripon_url=reverse('useripon')
    
    def test_login_url_exists(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'moneyapp/login.html')
    
    def test_login_success(self):
        response=self.client.post(self.login_url,self.user_correct,format='text/html')
        self.assertEqual(response.status_code, 200)
        #Status Code is 200 as Login Success redirects to Homepage.
    
    def test_login_empty(self):
        response=self.client.post(self.login_url,self.user_empty,format='text/html')
        self.assertEqual(response.status_code, 200)
        #Status Code is 200 as Login Empty redirects to Homepage.
        
    def test_login_fail(self):
        response=self.client.post(self.login_url,self.user_wrong,format='text/html')
        self.assertEqual(response.status_code, 200)
        #Status Code is 200 as Login Fail redirects to Homepage.
    
    def test_mainpage_url_exists(self):
        response = self.client.get(self.homepage_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'moneyapp/mainpage.html')

    def test_userprofile_url_exists(self):
        response = self.client.get(self.userprofile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'moneyapp/userprofile.html')

    def test_userbalances_url_exists(self):
        response = self.client.get(self.userbalances_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'moneyapp/userbalances.html')

    def test_useripon_url_exists(self):
        response = self.client.get(self.useripon_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'moneyapp/useripon.html')