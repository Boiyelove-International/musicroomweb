from django.db import models
from django.conf import settings
from model_utils.models import TimeStampedModel
from accounts.models import PartyGuest

User = settings.AUTH_USER_MODEL


# Create your models here.
class Event(TimeStampedModel):
	name = models.CharField(max_length=120)
	about = models.CharField(max_length = 320)
	event_time = models.TimeField()
	event_date = models.DateField()
	image = models.ImageField(upload_to="/event_images")
	organizer = models.ForeignKeyField(
		User, on_delete = models.CASCADE
		)
	attendees = models.ManyToManyField(PartyGuest
		)
	suggestions = models.ManyToManyField(SongSuggestions)

class Notification(TimeStampedModel):
	event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
	content = models.CharField(max_length = 120)
	organizer = models.ForeignKey(PartyGuest, on_delete=models.CASCADE, null=True )
	guest = models.ForeignKey(EventOrganizer, on_delete=models.CASCADE, null=True)


class SongSuggestion(TimeStampedModel):
	song_title = models.CharField(max_length=120)
	artist_name = models.CharField(max_length = 120)
	album_art = models.URLField()
	status = models.BooleanField(null=True)
	song_url = models.URLField(null=True)


"""
{
    'track_name': 'Marshmello Live at Lollapalooza 2021 ...', 
    'datePublished': '2021-08-04', 
    'track_Id': '8eXFvzMEldk', 
    'track_url': 'https://music.youtube.com/watch?v=8eXFvzMEldk', 
    'track_image': 'https://i.ytimg.com/vi/8eXFvzMEldk/hqdef...'
}
"""

class Song(TimeStampedModel):
	pass

class Playlist(TimeStampedModel):
	pass


