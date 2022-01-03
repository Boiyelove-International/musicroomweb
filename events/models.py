import uuid
from django.db import models
from django.conf import settings
from model_utils.models import TimeStampedModel
from ordered_model.models import OrderedModel
from accounts.models import PartyGuest, EventOrganizer


User = settings.AUTH_USER_MODEL


# Create your models here.
class Song(TimeStampedModel):
	song_title = models.CharField(max_length=120)
	artist_name = models.CharField(max_length = 120)
	album_art = models.URLField()
	song_url = models.URLField(null=True)
	play_count = models.PositiveIntegerField(default=0)
	apple_song_id = models.CharField(max_length=30, unique=True)
	suggestion_count = models.PositiveIntegerField(default=0)

	def __str__(self):
		return "%s - %s" % (self.song_title, self.artist_name)

	def suggestion_count(self):
		return SongSuggestion.objects.filter(song__apple_song_id = self.apple_song_id).count()

class Event(TimeStampedModel):
	name = models.CharField(max_length=120)
	about = models.CharField(max_length = 320)
	event_time = models.TimeField()
	event_date = models.DateField()
	event_ended = models.DateTimeField(null=True, blank=True)
	image = models.ImageField(upload_to="event_images")
	code = models.CharField(max_length=4, editable=False, default="ABCD")
	organizer = models.ForeignKey(
		User, on_delete = models.CASCADE, editable=False
		)
	attendees = models.ManyToManyField(PartyGuest, editable=False)

	def suggestions(self):
		return SongSuggestion.objects.filter(event = self)

	def playlist(self):
		ss = self.suggestions()
		if ss:
			ss = ss.filter(accepted = True)
		return ss


class SongSuggestion(TimeStampedModel, OrderedModel):
	event = models.ForeignKey(Event, on_delete=models.CASCADE)
	song = models.ForeignKey(Song, on_delete=models.CASCADE)
	accepted = models.BooleanField(null=True)
	is_playing = models.BooleanField(null=True) #Null  not played, playing = true, played = false
	suggested_by = models.ForeignKey(PartyGuest, on_delete=models.CASCADE)
	order_with_respect_to = ('event', 'created')

	# def play_next(self):
	# 	event = self.event
	# 	ss = event.suggestions()
	# 	self.




class Playlist(TimeStampedModel):
	pass




class Notification(TimeStampedModel):
	event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
	content = models.CharField(max_length = 120)
	organizer = models.ForeignKey(EventOrganizer, on_delete=models.CASCADE, null=True )
	guest = models.ForeignKey(PartyGuest, on_delete=models.CASCADE, null=True)


