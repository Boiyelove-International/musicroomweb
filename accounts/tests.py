import time
from datetime import datetime
from django.core import mail
from django.conf import settings
from django.urls import reverse, reverse_lazy
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import EventOrganizer, EmailAddress

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




		# test verify email with wrong email
		url = reverse('accounts:verify-email')
		data = dict(email = "testuser22@boiyelove.website", code=EmailAddress.objects.get().code)
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


		# test verify email with wrong code
		data = dict(email = "testuser@boiyelove.website", code="shfhhhre")
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

		# test verify email 
		data = dict(email = "testuser@boiyelove.website", code=EmailAddress.objects.get().code)
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(User.objects.get().email, "testuser@boiyelove.website")


		# Test forgot password step 1
		url = reverse('accounts:forgot-password', kwargs={'step': 'send_code'})
		data = dict(email='testuser@boiyelove.website')
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(PasswordResetRequest.objects.count(), 1)

		# Test forgot password step 2
		url = reverse('accounts:forgot-password', kwargs={'step': 'verify_code'})
		psr = PasswordResetRequest.objects.get()
		data = dict(email='testuser@boiyelove.website', code=psr.code)
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(PasswordResetRequest.objects.count(), 1)

		# Test forgot password step 3
		url = reverse('accounts:forgot-password', kwargs={'step': 'change_password'})
		data = dict(email='testuser@boiyelove.website', code=psr.code, new_password='examplepass')
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(User.objects.get().check_password("examplepass"), True)
		self.assertEqual(PasswordResetRequest.objects.get().used, True)
		self.assertEqual(PasswordResetRequest.objects.get().active, False)

	def test_send_mail(self):
		subject = "Test Mail " +  str(datetime.now())
		mail.send_mail(subject, "Here is the message",
			settings.DEFAULT_FROM_EMAIL, ['daahrmmieboiye@gmail.com'],
			fail_silently=False)
		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(mail.outbox[0].subject, subject)

