import base64
import pprint
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.mixins import DestroyModelMixin
from rest_framework.generics import  ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FileUploadParser, FormParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import EventSerializer, SongSuggestionSerializer, NotificationSerializer,  EventSerializerForm, SongSuggestionSerializer
from accounts.models import Device, PartyGuest
from .models import Event, SongSuggestion, Notification, Song
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


#API Schema Response Params & Responses
param_guest_id  = openapi.Parameter('HTTP_GUEST', in_=openapi.IN_HEADER, description='Guest Device Id', type=openapi.TYPE_STRING)
param_event_id   = openapi.Parameter('pk', in_=openapi.IN_PATH, description='Event Id', type=openapi.TYPE_STRING)
event_response = openapi.Response('Returns Event Object', EventSerializer)   

class SearchSongView(APIView):
	term = openapi.Parameter('term', in_=openapi.IN_QUERY, description='term',
                               type=openapi.TYPE_STRING)
	song_suggestion = openapi.Response('response description', SongSuggestionSerializer)   
	@swagger_auto_schema(
		manual_parameters=[term],
		tags=["search"],
		responses = {
			'200' : openapi.Response(
				description="Response 200",
				examples = {
				"application/json": [
				{
				"song_title": "Enyanda",
				"artist_name": "Sheebah",
				"song_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview125/v4/83/19/a7/8319a765-282d-3b50-9a6b-a227823c9f6a/mzaf_1832824329428830054.plus.aac.p.m4a",
				"album_art": "https://is4-ssl.mzstatic.com/image/thumb/Music114/v4/39/56/65/395665f4-a8ce-f4ab-94e4-a55bc061301c/859741319014_cover.jpg/300x300bb.jpg",
				"apple_song_id": "1527408985"
				}
				]}),
			'400': 'Bad Request'
		},		
		security=[],
		operation_id='Search Songs',
		operation_description='Search for song titles',
	)

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
	q = openapi.Parameter('q', in_=openapi.IN_QUERY, description='Event code',
                                type=openapi.TYPE_STRING)
	event_response = openapi.Response('Returns Event Object', EventSerializer)   
	@swagger_auto_schema(
		manual_parameters=[q],
		tags=["Get Event -  Party Guest"],
		responses = {
			'200' : event_response,
			'400': 'Bad Request',
			'404': openapi.Response(
				description="Response 404",
				examples = {
				"error": "Event not found"
				})
		},		
		security=[],
		operation_id='Get event by code',
		operation_description='Get data about an event a guest is about to join',
	)
	def get(self, request):
		q = request.GET.get("q", None)
		# print("q is ", q)
		event = Event.objects.filter(
			code = q).first()
		if event:
			s = EventSerializer(event, context={"request": request})
			# print("s data is", s.data)
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


	
	@swagger_auto_schema(
		manual_parameters=[param_guest_id, ],
		tags=["Join Event - Party Guest"],
		request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'event_code': openapi.Schema(type=openapi.TYPE_STRING, description='Event Code'),
        }),
		responses = {
		'200' : openapi.Response(
			description="Successful",
			examples = {
			"joined": "True"
			}),
		'400': openapi.Response(
			description="Response 404",
			examples = {
			"error": "Guest not found",
			"joined": False,
			}),
		'404': openapi.Response(
			description="Response 404",
			examples = {
			"error": "Event not found",
			"joined": False,
			})
		},		
		
		security=[],
		operation_id='Join Event',
		operation_description='Endpoint used to join event',
	)
	def post(self, request):
		headers = request.META.get("headers", None)
		guest_id =  None
		# pprint.pprint(request.META)
		if headers:
			guest_id = headers.get("HTTP_GUEST")
		else:
			guest_id = request.META.get("HTTP_GUEST")
		# pprint.pprint(request.META)
		if guest_id:
			device = Device.objects.filter(
				device_id = guest_id
				).first()
			# Get the device
			if device:
				# Get he user
				pg = PartyGuest.objects.filter(user = device).first()
				code =request.data.get("event_code", None)
				# Get the event
				event = Event.objects.filter(
					code = code).first()
				if event:
					# add as attendee
					s = event.attendees.add(pg)
					return Response(
						{"joined": True},
						status = status.HTTP_200_OK
						)
				else:
					return 	Response(
								{
								"error": "Event not found",
								"joined": False,
								},
								status = status.HTTP_404_NOT_FOUND
								)
		return 	Response(
		{
		"error": "Guest not found",
		"joined": False,
		},
		status = status.HTTP_400_BAD_REQUEST
			)



class EventCreateView(ListCreateAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = EventSerializerForm
	queryset = Event.objects.all()
	parser_classes = [JSONParser, MultiPartParser, FileUploadParser]


	# def get_serializer_class(self):
	# 	if self.request.method == "GET":
	# 		return EventSerializer
	# 	return self.serializer_class

	# @swagger_auto_schema(mwethod="POST", request_body=openapi.Schema(
 #        type=openapi.TYPE_OBJECT,
 #        properties={
 #            'namer': openapi.Schema(type=openapi.TYPE_STRING, description='The desc'),
 #            'body': openapi.Schema(type=openapi.TYPE_STRING, description='The desc'),
 #        }))


	q = openapi.Parameter('q', in_=openapi.IN_QUERY, description='Query',
                               type=openapi.TYPE_STRING)
	@swagger_auto_schema(
		manual_parameters=[param_guest_id, ],
		tags=["Get Event List - Event organizer / PartyGuest"],
		responses = {
		'200' : event_response,
		},		
		
		# security=[],
		operation_id='Get Event',
		permission_classes = [IsAuthenticated],
		operation_description='Get event details by name',
	)
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

		endpoint_data = EventSerializer(qs, many=True, context={'request': request})
		return Response(
			endpoint_data.data,
			status = status.HTTP_200_OK
			)	


	# @swagger_auto_schema(
	
	# 	tags=["Create an Event"],
	# 	responses = {
	# 	'200' : event_response,
	# 	},		
		
	# 	# security=[],
	# 	operation_id='Create Event',
	# 	permission_classes = [IsAuthenticated],
	# 	operation_description='Create an Event',
	# )

	# @swagger_auto_schema(operation_description="POST /articles/{id}/image/")
	# def create(self, request, *args, **kwargs):
	# 	return super(EventCreateView, self).create(request, *args, **kwargs)

	def perform_create(self, serializer):
		serializer.save(organizer = self.request.auth.user)


	# def post(self, request):
	# 	errors = {}
	# 	image = request.data.pop("image", None)
	# 	data = request.data
	# 	serializer = EventSerializerForm(data=data)
	# 	if serializer.is_valid(raise_exception=True):
	# 		if image:
	# 			decoded_file = ContentFile(base64.decodebytes(bytes(image['file'], 'utf-8')), name=image['filename'])
	# 			data.update(image=image)
	# 			event = Event(
	# 				name = data["name"],
	# 				about = data["about"],
	# 				event_time = data["event_time"],
	# 				event_date= data["event_date"],)
	# 			event.organizer = request.auth.user
	# 			event.image.save(name=image["filename"], content=decoded_file)
	# 			# u = User.objects.get(username = request.auth.user)
	# 			# event.organizer = user
	# 			event = event.save()
	# 			serializer = EventSerializer(event)
	# 			return Response(
	# 			serializer.data,
	# 			status = status.HTTP_201_CREATED
	# 			)
	# 		else:
	# 			errors["image"] = "Please provide an image"
	# 	else:
	# 		errors.update(
	# 			serializer.errors)
	# 	return Response(
	# 		serializer.errors,
	# 		status = status.HTTP_400_BAD_REQUEST
	# 		)	





class EventDetailView(RetrieveUpdateDestroyAPIView):
	permission_class = [IsAuthenticated]
	serializer_class = EventSerializer
	queryset = Event.objects.all()
	parser_classes = [JSONParser, MultiPartParser, FileUploadParser]



class SuggestionListView(ListAPIView):
	serializer_class = SongSuggestionSerializer
	queryset = SongSuggestion.objects.all()

	def get_queryset(self):
		qt = self.request.GET.get("qt", None)
		qs = super().get_queryset()
		if qt:
			pass
		return qs



class SuggestionUpdate(APIView):
	serializer_class = SongSuggestionSerializer
	queryset = SongSuggestion.objects.all()
	# http_method_names = ['put', 'patch', 'delete']
	"""
	Suggest song - Create - put
	Accept - Reject -  Update -  patch
	Remove suggestion - delete - delete
	"""


	def get_party_guest(self):
		# Check user
		headers = self.request.META.get("headers", None)
		guest_id = self.request.META.get("HTTP_GUEST") or headers.get("HTTP_GUEST")
		pg = None

		if guest_id:
			device = Device.objects.filter(
				device_id = guest_id
				).first()
			if device:
				pg = PartyGuest.objects.filter(user = device).first()
				self.pg = pg
		return pg


	def get(self, request, *args, **kwargs):

		# Check user
		if self.get_party_guest():
			#Check event
			event_id = kwargs.get("pk",None)
			
			try:
				event = Event.objects.get(id= event_id)
				ss = SongSuggestion.objects.filter(event = event, suggested_by = self.pg)
				ss = SongSuggestionSerializer(ss, many=True)
				return Response(
				ss.data,
				status = status.HTTP_200_OK)
			except ObjectDoesNotExist:
				return Response(
					{"detail": "Event not found"},
					status = status.HTTP_404_NOT_FOUND)
		return Response(
				{"detail": "Guest Permission required"},
				status = status.HTTP_400_BAD_REQUEST)


	@swagger_auto_schema(
		manual_parameters=[param_guest_id, param_event_id ],
		tags=["Suggest a song"],
		responses = {
			'200' : SongSuggestionSerializer,
			'404': openapi.Response(
				description="Response 404",
				examples = {
				"application/json": {"detail": "Item not found"}}),
			'400': openapi.Response(
				description="Response 400",
				examples = {
				"application/json": {"detail": "Guest Permission required"}}),
		},		
		
		# security=[],
		operation_id='Suggest Song',
		operation_description='Suggest a song for an event',
	)	
	def put(self, request, *args, **kwargs):
		"""
		Suggest song - Create - put
		"""

		# Check user
		if self.get_party_guest():
			#Check event
			event_id = kwargs.get("pk",None)
			try:
				apple_song_id = request.data.get("apple_song_id", None)
				event = Event.objects.get(id= event_id)
				song = Song.objects.get(apple_song_id = apple_song_id)
				ss = SongSuggestion.objects.filter(
					event = event,
						song = song
					)
				if ss.exists():
					ss = ss.first()
					ss = SongSuggestionSerializer(ss)
					return Response(
					ss.data,
					status = status.HTTP_200_OK)
				else:
					ss = SongSuggestion.objects.create(
						event = event,
						song = song,
						suggested_by = self.pg)
				if ss:
					ss = SongSuggestionSerializer(ss)
					return Response(
					ss.data,
					status = status.HTTP_201_CREATED)
			except ObjectDoesNotExist:
				return Response(
					{"detail": "Item not found"},
					status = status.HTTP_404_NOT_FOUND)
		return Response(
				{"detail": "Guest Permission required"},
				status = status.HTTP_400_BAD_REQUEST)


	def patch(self, request, *args, **kwargs):
		"""
		Accept - Reject -  Update -  patch
		"""
		if request.user.is_authenticated:
			# Check user
			try:
				#Check event
				pk = kwargs.get("pk",None)
				#Todo: Check if user is owner
				spk = request.data.get("suggestion_id", None)

				play_song = request.data.get("play_song", None)
				if play_song:
					pass

				play_song_next = request.data.get("play_song_next", None)
				if play_song_next:
					pass

				ss = SongSuggestion.objects.get(id = spk)
				accepted = request.data.get("accept_suggestion", None)
				if accepted != None:
					ss.accepted = accepted
					ss.save()
					return Response(
						{"detail": "Suggestion updated"},
						status = status.HTTP_200_OK)
			except ObjectDoesNotExist:
				return Response(
					{"detail": "Item not found"},
					status = status.HTTP_404_NOT_FOUND)
		return Response(
				{"detail": "Permission required"},
				status = status.HTTP_400_BAD_REQUEST)

	def delete(self, request, *args, **kwargs):
		"""
		Remove suggestion - delete - delete
		"""

		# Check user
		if self.get_party_guest():
			#Check event
			pk = kwargs.get("pk", None)
			spk = request.data.get("suggestion_id", None)
			ss=SongSuggestion.objects.filter(id = spk,
						event = Event.objects.get(id = pk),
						suggested_by = self.pg).first()
			if ss:
				ss.delete()
				# if the resoonse is 204, don't proses the  json
				return Response(
					status = status.HTTP_204_NO_CONTENT)
			return Response(
				{"detail": "Item not found"},
				status = status.HTTP_404_NOT_FOUND)
		return Response(
				{"detail": "Guest Permission required"},
				status = status.HTTP_400_BAD_REQUEST)


class NotificationListView(ListAPIView):
	serializer_class = NotificationSerializer
	queryset = Notification.objects.all()
