import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import EventOrganizer, Device, PartyGuest
from .utils import generateCode

User = get_user_model()

class UserFactory(DjangoModelFactory):
	first_name = factory.Faker('first_name')
	email = factory.LazyAttributeSequence(lambda o, n: '%s_%s@boiyelove.website' % (o.first_name, n))
	username = factory.LazyAttributeSequence(lambda o, n: '%s_%s' % (o.first_name, n))
	password = factory.PostGenerationMethodCall('set_password', 'somePasswordHere')

	class Meta:
		model = User




class DeviceFactory(DjangoModelFactory):
	device_name = factory.Faker('word')
	device_id = factory.LazyAttributeSequence(lambda o, n: "%s_%s" % (o.device_name, generateCode(limit=10 + n)))

	class Meta:
		model = Device
		
class PartyGuestFactory(DjangoModelFactory):
	user = factory.SubFactory(DeviceFactory)
	display_name = factory.Faker('first_name')
	# profile_photo =  factory.django.ImageField(color="red")

	class Meta:
		model = PartyGuest



		