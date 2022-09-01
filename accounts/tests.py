import pprint
import time
import shutil
import tempfile
from datetime import datetime
from django.core import mail
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import EventOrganizer, EmailAddress, PartyGuest, Device, PasswordResetRequest
from .factories import PartyGuestFactory

# Create your tests here.
# factory = APIRequestFactory()
# request = factory.post("url", dict(data), §mat="json")


TEST_DIR = "test_data"


@override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
class AccountAPITestCase(APITestCase):

	def test_api_create_account(self):
		"""
		Ensure we can create account
		# """
		# eo = EventOrganizerFactory()
		pg = PartyGuestFactory()
		url = reverse('accounts:register-organizer')
		data = dict(display_name="Userperson", email="testuser@boiyelove.website", password="Somepassword123!")
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(User.objects.count(), 1)
		user = User.objects.get(email = "testuser@boiyelove.website")
		self.assertEqual(user.email, "testuser@boiyelove.website")
		self.assertEqual(user.check_password("Somepassword123!"), True)
		self.assertEqual(EventOrganizer.objects.count(), 1)
		self.assertEqual(EventOrganizer.objects.get(user=user).display_name, "Userperson")
		self.assertEqual(Token.objects.count(), 1)

		#test user can't registter twice
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(User.objects.count(), 1)

		#test login
		url = reverse('accounts:login-user')
		data = dict(username="testuser@boiyelove.website", password="Somepassword123!")
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		#test social login create account
		data = 	{
		"social": "facebook",
		"access_token": "gfdsfghjjfdffhgjhj",
		"id_token": "dfdgfhgjhkdf",
		"email": "social@boiyelove.website",
		"name": "Social User",
		"image_url": "https://picsum.photos/id/237/200/300"
		}
		response = self.client.post(url, data, format='json')
		# pprint.pprint(response.json())
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		#test social login no error on repeat create account
		response = self.client.post(url, data, format='json')
		# pprint.pprint(response.json())
		self.assertEqual(response.status_code, status.HTTP_200_OK)


		#test forgot password with invalid data
		data = {
		"email": "testuser1234543212345@boiyelove.website"
		}
		url = reverse('accounts:forgot-password', kwargs={"step":"send_code"})
		response = self.client.post(url, data, format='json')
		# print(response.json())
		# pprint.pprint(response.json())
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(PasswordResetRequest.objects.count(), 0)


		url = reverse('accounts:forgot-password', kwargs={"step":"verify_code"})
		data = dict(email="testuser@boiyelove.website", code = "erthhgfd")
		response = self.client.post(url, data, format='json')
		# pprint.pprint(response.json())
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(PasswordResetRequest.objects.count(), 0)


		url = reverse('accounts:forgot-password', kwargs={"step":"change_password"})
		data = dict(email="testuser@boiyelove.website", code = "dfgfd", new_password="Whohelpme123")
		response = self.client.post(url, data, format='json')
		# pprint.pprint(response.json())
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(PasswordResetRequest.objects.count(), 0)



		#test forgot password with valid data
		data = {
		"email": "testuser@boiyelove.website"
		}
		url = reverse('accounts:forgot-password', kwargs={"step":"send_code"})
		response = self.client.post(url, data, format='json')
		# print(response.json())
		# pprint.pprint(response.json())
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(PasswordResetRequest.objects.count(), 1)


		url = reverse('accounts:forgot-password', kwargs={"step":"verify_code"})
		pr = PasswordResetRequest.objects.get()
		data = dict(email="testuser@boiyelove.website", code = pr.code)
		response = self.client.post(url, data, format='json')
		# pprint.pprint(response.json())
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(PasswordResetRequest.objects.count(), 1)


		url = reverse('accounts:forgot-password', kwargs={"step":"change_password"})
		data = dict(email="testuser@boiyelove.website", code = pr.code, new_password="Whohelpme123")
		response = self.client.post(url, data, format='json')
		# pprint.pprint(response.json())
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(PasswordResetRequest.objects.count(), 1)
		u = User.objects.get(email="testuser@boiyelove.website")
		self.assertTrue(u.check_password("Whohelpme123"))






	def test_send_mail(self):
		subject = "Test Mail " +  str(datetime.now())
		mail.send_mail(subject, "Here is the message",
			settings.DEFAULT_FROM_EMAIL, ['daahrmmieboiye@gmail.com'],
			fail_silently=False)
		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(mail.outbox[0].subject, subject)

	def test_party_guest_create_account(self):
		url = reverse('accounts:register-guest')
		data = dict(display_name="milo", 
			device_id="werwsdf123", device_name="somedevicename")
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Device.objects.count(), 1)
		self.assertEqual(PartyGuest.objects.count(), 1)

		pg = PartyGuestFactory()
		self.assertEqual(PartyGuest.objects.count(), 2)
		self.assertTrue(type(pg) is PartyGuest)



def tearDownModule():
    print("\nDeleting temporary files...\n")
    try:
        shutil.rmtree(TEST_DIR)
    except OSError:
        pass
