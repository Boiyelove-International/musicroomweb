import time
from datetime import datetime
import factory
from factory.django import DjangoModelFactory
from accounts.factories import UserFactory
from .models import Event


class EventFactory(DjangoModelFactory):
	name = factory.Faker('word')
	about = factory.Faker('sentence')
	event_time = factory.LazyFunction(lambda: datetime.now())
	event_date = factory.LazyFunction(datetime.today)
	image = factory.django.FileField(color="blue")
	organizer = factory.SubFactory(UserFactory)

	class Meta:
		model = Event


# class SongSuggestion(TimeStampedModel):
# 	event = models.ForeignKey(Event, on_delete=models.CASCADE)
# 	song = models.ForeignKey(Song, on_delete=models.CASCADE)
# 	is_playing = models.BooleanField(null=True) #Null
