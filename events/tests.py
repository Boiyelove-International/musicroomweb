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
	tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
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
		file1 = open("media/test_files/" + "test_image.jpeg", 'rb')
		file1_read = file1.read()
		file_encode = base64.encodebytes((file1_read))


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




		# test without search_tag or document



		# test update event
		url = reverse('events:events-detail-update-delete', kwargs={"pk":response_data["id"]})
		print("data is", data, type(data))
		data["name"]='House Party 2 Edited'
		data["image"] = generate_image()
		response = self.client.patch(url, data, format='multipart')
		print(response.json())
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(Event.objects.count(), 1)

