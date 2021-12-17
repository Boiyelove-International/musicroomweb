from rest_framework.generics import  ListAPIView
from .serializers import EventSerializer, SongSuggestionSerializer, NotificationSerializer
from .models import
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

class SearchView(APIView):

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

class EventCreateList(ListCreateAPIView):
	serializer_class = EventSerializer
	queryset = EventSerializer.objects.all()

class EventDetail(RetrieveUpdateDestroyAPIView):
	serializer_class = EventSerializer
	queryset = EventSerializer.objects.all()


class SuggestionsList(ListAPIView):
	serializer_class = SongSuggestionSerializer
	queryset = SongSuggestionSerializer.objects.all()


class SuggestionUpdate(RetrieveUpdateDestroyAPIView):
	serializer_class = SongSuggestionSerializer
	queryset = SongSuggestionSerializer.objects.all()	


class NotificationListView(ListAPIView):
	serializer_class = NotificationSerializer
	queryset = Notification.objects.all()
