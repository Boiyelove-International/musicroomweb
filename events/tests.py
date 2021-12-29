import os
import base64
import shutil
import tempfile
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework import status
from accounts.tests import AccountAPITestCase
from accounts.factories import PartyGuestFactory, UserFactory
from .factories import EventFactory
from .models import Song, Event, SongSuggestion
from .utils import search_music

# Create your tests here.

# Create an event
# Edit an event
# Join an event
# Search for song
# Suggest a song
# Accept Suggestion
# Deny Suggestion
# Remove suggestion - Party Guest

def generate_image():
	bts = BytesIO()
	image = Image.new("RGB", (300,300))
	image.save(bts, 'jpeg')
	return SimpleUploadedFile('test.jpeg', bts.getvalue())

class SongTests(APITestCase):
	def test_no_duplicate_songs_created(self):
		result1 = search_music("davido fia")
		previous_count = len(result1)
		previous_model_count = Song.objects.all().count()
		result2 = search_music("davido fia")
		self.assertEqual(previous_model_count, Song.objects.all().count())

class EventTests(APITestCase):
	# def setUp(self):
	# 	if "test_media" not in settings.MEDIA_ROOT:
	# 		settings.MEDIA_ROOT = os.path.join(settings.MEDIA_ROOT, 'test_media')
			


	# def tearDown(self):
	# 	shutil.rmtree(settings.MEDIA_ROOT)

	def test_create_event(self):
		user = UserFactory()
		pg = PartyGuestFactory()
		token = Token.objects.get(user=user)

		event = EventFactory()
		self.assertEqual(Event.objects.count(), 1)
		self.assertTrue(type(event) is Event)

		tmp_file = generate_image()
		data = dict(name='House Party',
			about= "This is a house party come celebrate with us",
			event_date = "2021-11-23",
			event_time = "11:22 AM",
			image = tmp_file
			)


		url = reverse('events:events-list-create')
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
		# test created event
		response = self.client.post(url, data, format='multipart')
		response_data = response.json()
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Event.objects.count(), 2)


		# test update event
		url_2= reverse('events:events-detail-update-delete', kwargs={"pk":response_data["id"]})
		response = self.client.get(url_2, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)


		# test update event
		url_2= reverse('events:events-detail-update-delete', kwargs={"pk":response_data["id"]})
		data["name"]='House Party 2 Edited'
		# file1 = open("media/test_files/" + "test_image.jpeg", 'rb')
		data["image"] = generate_image()
		response = self.client.patch(url_2, data, format='multipart')
		# print("response.json is", response.json())
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(Event.objects.count(), 2)


		# test returns the right length of data
		url_3 = reverse('events:events-list-create')
		response = self.client.get(url_3, format='json')
		self.assertEqual(len(response.json()), 1)

		#test delete event
		url_2= reverse('events:events-detail-update-delete', kwargs={"pk":response_data["id"]})
		data["image"] = generate_image()
		response = self.client.delete(url_2, data, format='multipart')
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(Event.objects.count(), 1)



	def test_search_song(self):
		url = reverse('events:search') + "?term=Davido Fia"
		response = self.client.get(url, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_accept_suggestion(self):
		pg = PartyGuestFactory()
		headers = {"HTTP_GUEST": pg.user.device_id}
		event = EventFactory()

		url = reverse('events:search') + "?term=Davido Fia"
		response = self.client.get(url, headers=headers, format="json")
		data_list = response.json()

		data = {"apple_song_id": data_list[2]["apple_song_id"]}

		url = reverse("events:events-suggestions", kwargs={"pk": event.id})
		response = self.client.put(url, data, headers=headers, format="json")
		ss = response.json()
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)


		token = Token.objects.get(user=event.organizer)
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
		url = reverse("events:events-suggestions", kwargs={"pk": event.id})
		data = {"accept_suggestion": True, "suggestion_id": ss["id"]}
		response = self.client.patch(url, data, format="json")
		print(response.json())
		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_deny_suggestion(self):
		pg = PartyGuestFactory()
		headers = {"HTTP_GUEST": pg.user.device_id}
		event = EventFactory()

		url = reverse('events:search') + "?term=Davido Fia"
		response = self.client.get(url, headers=headers, format="json")
		data_list = response.json()

		data = {"apple_song_id": data_list[2]["apple_song_id"]}

		url = reverse("events:events-suggestions", kwargs={"pk": event.id})
		response = self.client.put(url, data, headers=headers, format="json")
		ss = response.json()
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)


		token = Token.objects.get(user=event.organizer)
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
		url = reverse("events:events-suggestions", kwargs={"pk": event.id})
		data = {"accept_suggestion": False, "suggestion_id": ss["id"]}
		response = self.client.patch(url, data, format="json")
		print(response.json())
		self.assertEqual(response.status_code, status.HTTP_200_OK)


class PartyGuestEventTests(APITestCase):

	def test_join_an_event(self):
		pg = PartyGuestFactory()
		headers = {"HTTP_GUEST": pg.user.device_id}
		url = reverse("events:join-event")
		event = EventFactory()
		self.assertTrue(type(event) is Event)
		response = self.client.get(url + "?q=%s" % event.code, headers=headers, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		#Todo: Add header authentication for guests
		
		response = self.client.post(url, headers=headers,  data={"event_code": event.code}, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(pg in event.attendees.all())
		#Todo: check if partyguest is a part of event_attendees


	def test_view_event(self):
		pg = PartyGuestFactory()
		headers = {"HTTP_GUEST": pg.user.device_id}
		event = EventFactory()
		url = reverse("events:events-detail-update-delete", kwargs={"pk": event.id})
		response = self.client.get(url, headers=headers,)
		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_search_song(self):
		pg = PartyGuestFactory()
		headers = {"HTTP_GUEST": pg.user.device_id}
		url = reverse('events:search') + "?term=Davido Fia"
		response = self.client.get(url, headers=headers, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)


	def test_suggest_song_and_remove_song_suggestion(self):
		pg = PartyGuestFactory()
		headers = {"HTTP_GUEST": pg.user.device_id}
		event = EventFactory()

		url = reverse('events:search') + "?term=Davido Fia"
		response = self.client.get(url, headers=headers, format="json")
		data_list = response.json()

		data = {"apple_song_id": data_list[0]["apple_song_id"]}

		url = reverse("events:events-suggestions", kwargs={"pk": event.id})
		response = self.client.put(url, data, headers=headers, format="json")
		# print(response.json())
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(SongSuggestion.objects.all().count(), 1)
		self.assertEqual(SongSuggestion.objects.all().first().song.apple_song_id, data_list[0]["apple_song_id"])
		#Todo must be attendee before suggesting



		# test remove suggestion
		url = reverse("events:events-suggestions", kwargs={"pk": event.id})
		data = {"suggestion_id": SongSuggestion.objects.all().first().id}
		response = self.client.delete(url, data, headers=headers, format="json")
		# print(response.json())
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		#Todo: Test already suggested

