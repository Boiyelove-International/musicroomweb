import base64
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import  ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import EventSerializer, SongSuggestionSerializer, NotificationSerializer,  EventSerializerForm
from accounts.models import Device, PartyGuest
from .models import Event, SongSuggestion, Notification
from .utils import search_music


"""
# Events
- Create
- Edit
- Delete
- Join
- Suggest a song
- Accept / Deny Suggestion
- Remove suggestion - PG
- Play Song
- Facebook sign up / Sign in
- Google sign up / sing in
- Apple sign up / sign in


- Search: GET https://api.music.apple.com/v1/catalog/{storefront}/search
?term=q.replace(" ", "+")
Query Parameters
Default: 25
Maximum Value: 25

SearchResponse.Results.SongsSearchResult
The songs results for a term search for specific resource types.
Songs, href, next


Songs
id, type, href

Songs.Attributes
artistName, artwork, name,  previews

Preview
artwork, url, hlsUrl

- Song: GET https://api.music.apple.com/v1/catalog/{storefront}/songs/{id}

Responses, 200, 401, 500

Storefront = IP to location to country code to lowercase
"""

# List all my events (Events I created or events I joined)
# List all all - All events there are
# List all notifications - ones I got from events and suggestions

class SearchSongView(APIView):

	def get(self, request):
		term = request.GET.get('term', None)
		endpoint_data = {}
		if not term:
			
			return Response(
					endpoint_data,
					status = status.HTTP_404_NOT_FOUND
					)
		endpoint_data = search_music(term)
		return Response(
			endpoint_data,
			status = status.HTTP_200_OK
			)	


class JoinEventView(APIView):
	def get(self, request):
		q = request.GET.get("q", None)
		print("q is ", q)
		event = Event.objects.filter(
			code = q).first()
		if event:
			s = EventSerializer(event)
			print("s data is", s.data)
			return Response(
				s.data,
				status = status.HTTP_200_OK
				)
		return 	Response(
				{
				"error": "Event not found"
				},
				status = status.HTTP_404_NOT_FOUND
				)

	def post(self, request):
		return Response(
			{},
			status = status.HTTP_200_OK
			)


class EventCreateView(APIView):
	permission_class = [IsAuthenticated]
	serializer_class = EventSerializer
	queryset = Event.objects.all()


	def get(self, request):
		qs = Event.objects.all()
		if request.auth:
			qs = qs.filter(organizer = request.auth.user)
		else:
			guest_id = request.META.get("HTTP_GUEST")
			if guest_id:
				device = Device.objects.filter(
					device_id = guest_id
					).first()
				if device:
					pg = PartyGuest.objects.filter(user = device).first()
					qs = Event.objects.filter(attendees=pg)
			print("guest is ", guest_id)
		q = request.GET.get("q", None)
		if q:
			qs = qs.filter(name__icontains = q)

		endpoint_data = EventSerializer(qs, many=True)
		return Response(
			endpoint_data.data,
			status = status.HTTP_200_OK
			)	

	def post(self, request):
		errors = {}
		image = request.data.pop("image", None)
		data = request.data
		serializer = EventSerializerForm(data=data)
		if serializer.is_valid(raise_exception=True):
			if image:
				decoded_file = ContentFile(base64.decodebytes(bytes(image['file'], 'utf-8')), name=image['filename'])
				data.update(image=image)
				event = Event(
					name = data["name"],
					about = data["about"],
					event_time = data["event_time"],
					event_date= data["event_date"],)
				event.organizer = request.auth.user
				event.image.save(name=image["filename"], content=decoded_file)
				# u = User.objects.get(username = request.auth.user)
				# event.organizer = user
				event = event.save()
				serializer = EventSerializer(event)
				return Response(
				serializer.data,
				status = status.HTTP_201_CREATED
				)
			else:
				errors["image"] = "Please provide an image"
		else:
			errors.update(
				serializer.errors)
		return Response(
			serializer.errors,
			status = status.HTTP_400_BAD_REQUEST
			)	




class EventDetailView(RetrieveUpdateDestroyAPIView):
	permission_class = [IsAuthenticated]
	serializer_class = EventSerializer
	queryset = Event.objects.all()




class SuggestionsList(ListAPIView):
	serializer_class = SongSuggestionSerializer
	queryset = SongSuggestion.objects.all()


class SuggestionUpdate(RetrieveUpdateDestroyAPIView):
	serializer_class = SongSuggestionSerializer
	queryset = SongSuggestion.objects.all()	


class NotificationListView(ListAPIView):
	serializer_class = NotificationSerializer
	queryset = Notification.objects.all()
