import base64
import tempfile
from PIL import Image
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework import status
from accounts.tests import AccountAPITestCase
from accounts.factories import EventOrganizerFactory, PartyGuestFactory
from .models import Song, Event
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
	image = Image.new("RGB", (300,300))
	tmp_file = tempfile.NamedTemporaryFile(suffix=".png")
	image.save(tmp_file)
	return tmp_file.seek(0)

class SongTests(APITestCase):
	def test_no_duplicate_songs_created(self):
		result1 = search_music("davido fia")
		previous_count = len(result1)
		previous_model_count = Song.objects.all().count()
		result2 = search_music("davido fia")
		self.assertEqual(previous_model_count, Song.objects.all().count())

class EventTests(APITestCase):
	def test_create_event(self):
		eo = EventOrganizerFactory()
		pg = PartyGuestFactory()
		token = Token.objects.get(user=eo.user)



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
		self.assertEqual(Event.objects.count(), 1)


		# test update event
		url_2= reverse('events:events-detail-update-delete', kwargs={"pk":response_data["id"]})
		response = self.client.get(url_2, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)


		# test update event
		url_2= reverse('events:events-detail-update-delete', kwargs={"pk":response_data["id"]})
		data["name"]='House Party 2 Edited'
		file1 = open("media/test_files/" + "test_image.jpeg", 'rb')
		data["image"] = file1
		response = self.client.patch(url_2, data, format='multipart')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(Event.objects.count(), 1)


		#test delete event
		url_2= reverse('events:events-detail-update-delete', kwargs={"pk":response_data["id"]})
		data["image"] = file1
		response = self.client.delete(url_2, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(Event.objects.count(), 0)


	def test_search_song(self):
		url = reverse('events:search') + "?term=Davido Fia"
		response = self.client.get(url, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_suggest_song(self):
		pass

	def test_accept_suggestion(self):
		pass

	def test_deny_suggestion(self):
		pass

	def test_remove_suggestion(self):
		pass


class PartyGuestEventTests(APITestCase):
	def setUp(self):
		self.event = None
		self.pg = PartyGuestFactory()
		self.eo = EventOrganizerFactory()

	def test_join_an_event(self):
		url = reverse("events:join-event")
		'event/join/'
		pass

	def test_view_event(self):
		pass

	def test_suggest_song(self):
		pass

	def test_accept_suggestion(self):
		pass

	def test_deny_suggestion(self):
		pass

	def test_remove_suggestion(self):
		pass
