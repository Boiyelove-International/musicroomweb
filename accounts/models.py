from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from model_utils.models import TimeStampedModel

# Create your models here.
class EventOrganizer(TimeStampedModel):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	display_name = models.CharField(max_length=60)

class Device(TimeStampedModel):
	pass
		
class PartyGuest(TimeStampedModel):
	user = models.OneToOneField(Device, on_delete=models.CASCADE)
	display_name = display_name = models.CharField(max_length=60)
