import time
from datetime import datetime
import factory
from factory.django import DjangoModelFactory
from accounts.factories import UserFactory, PartyGuestFactory
from .models import Event



class EventFactory(DjangoModelFactory):
	name = factory.Faker('word')
	about = factory.Faker('sentence')
	event_time = factory.LazyFunction(lambda: datetime.now())
	event_date = factory.LazyFunction(datetime.today)
	# image = factory.django.ImageField(color="blue")
	organizer = factory.SubFactory(UserFactory)
	attendees = factory.RelatedFactoryList(
        PartyGuestFactory)

	class Meta:
		model = Event


	@factory.post_generation
	def attendees(self, create, extracted, **kwargs):
		if not create:
			# Simple build, do nothing.
			return
		if extracted:
			# A list of products were passed in, use them
			for pg in extracted:
				self.attendees.add(pg)


# class SongSuggestion(TimeStampedModel):
# 	event = models.ForeignKey(Event, on_delete=models.CASCADE)
# 	song = models.ForeignKey(Song, on_delete=models.CASCADE)
# 	is_playing = models.BooleanField(null=True) #Null
