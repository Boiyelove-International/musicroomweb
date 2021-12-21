import uuid
from django.db import models
from django.conf import settings
from model_utils.models import TimeStampedModel
from accounts.models import PartyGuest, EventOrganizer

User = settings.AUTH_USER_MODEL


# Create your models here.
class SongSuggestion(TimeStampedModel):
	song_title = models.CharField(max_length=120)
	artist_name = models.CharField(max_length = 120)
	album_art = models.URLField()
	status = models.BooleanField(null=True)
	song_url = models.URLField(null=True)
	is_playing = models.BooleanField(null=True) #Null  not played, playing = true, played = false


class Song(TimeStampedModel):
	song_title = models.CharField(max_length=120)
	artist_name = models.CharField(max_length = 120)
	album_art = models.URLField()
	status = models.BooleanField(null=True)
	song_url = models.URLField(null=True)

class Playlist(TimeStampedModel):
	pass

class Event(TimeStampedModel):
	name = models.CharField(max_length=120)
	about = models.CharField(max_length = 320)
	event_time = models.TimeField()
	event_date = models.DateField()
	image = models.ImageField(upload_to="event_images")
	code = models.CharField(max_length=4, editable=False, default="ABCD")
	organizer = models.ForeignKey(
		User, on_delete = models.CASCADE
		)
	attendees = models.ManyToManyField(PartyGuest)
	suggestions = models.ManyToManyField(SongSuggestion)

class Notification(TimeStampedModel):
	event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
	content = models.CharField(max_length = 120)
	organizer = models.ForeignKey(EventOrganizer, on_delete=models.CASCADE, null=True )
	guest = models.ForeignKey(PartyGuest, on_delete=models.CASCADE, null=True)


