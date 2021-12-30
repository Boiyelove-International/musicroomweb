from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from accounts.models import EventOrganizer
from accounts.serializers import PartyGuestSerializer
from .models import Event, SongSuggestion, Notification, Song



class SongSerializer(serializers.ModelSerializer):
	class Meta:
		model = Song
		fields = "__all__"


class SongSuggestionSerializer(serializers.ModelSerializer):
	class Meta:
		model = SongSuggestion
		fields = "__all__"
		depth = 1

class EventSerializerForm(serializers.ModelSerializer):
	class Meta:
		model = Event
		fields = ["id","name", "image", "about", "event_date", "code", "event_time",]


		

class EventSerializer(serializers.ModelSerializer):
	suggestions = SongSuggestionSerializer(many=True)
	organizer_display_picture = serializers.SerializerMethodField('get_organizer_picture')
	organizer = serializers.SerializerMethodField('get_organizer_display_name')
	image = serializers.SerializerMethodField("get_image_url")
	attendees = PartyGuestSerializer(many=True, read_only=True)

	class Meta:
		model = Event
		fields = "__all__"


	def get_image_url(self, obj):
		request = self.context.get('request')
		if obj.image and hasattr(obj.image, 'url'):
			url = obj.image.url
			if request:
				return request.build_absolute_uri(url)
			else:
				return url
		else:
			return None




	def get_organizer_picture(self, obj):
		eo = EventOrganizer.objects.filter(
			user = obj.organizer).first()
		if eo and eo.profile_photo:
			return eo.profile_photo.url
		return None

	def get_organizer_display_name(self, obj):
		eo = EventOrganizer.objects.filter(
			user = obj.organizer).first()
		return eo.display_name


class NotificationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Notification
		fields = "__all__"



class SearchSerializer(serializers.Serializer):
	term =  serializers.CharField(max_length = 60)