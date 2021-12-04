import time
from datetime import datetime
from django.core import mail
from django.conf import settings
from django.urls import reverse, reverse_lazy
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import EventOrganizer

# Create your tests here.
# factory = APIRequestFactory()
# request = factory.post("url", dict(data), format="json")


class AccountAPITestCase(APITestCase):

	def test_api_create_account(self):
		"""
		Ensure we can create account
		"""
		url = reverse('accounts:register-users')
		data = dict(display_name="Userperson", email="testuser@boiyelove.website", password="somenewpassword")
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(User.objects.count(), 1)
		user = User.objects.get(email = "testuser@boiyelove.website")
		self.assertEqual(user.email, "testuser@boiyelove.website")
		self.assertEqual(user.check_password("somenewpassword"), True)
		self.assertEqual(EventOrganizer.objects.count(), 1)
		self.assertEqual(EventOrganizer.objects.get(user=user).display_name, "Userperson")
		self.assertEqual(Token.objects.count(), 1)

		#test login
		url = reverse('accounts:login-user')
		data = dict(username="testuser@boiyelove.website", password="somenewpassword")
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
