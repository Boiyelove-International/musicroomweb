from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Event, SongSuggestion, Notification


class EventSerializerForm(serializers.ModelSerializer):
	class Meta:
		model = Event
		fields = ["name", "about", "event_date", "event_time"]
		

class EventSerializer(serializers.ModelSerializer):
	accepted_suggestions = serializers.SerializerMethodField('accepted_suggestions')
	organizer_display_picture = serializers.SerializerMethodField('get_organizer_picture')

	class Meta:
		model = Event
		fields = "__all__"


	def accepted_suggestions(self, obj):
		suggestions = obj.suggestions.all()
		if suggestions:
			return suggestions.filter(status=True).count()
		else:
			return 0

	def get_organizer_picture(self, obj):
		eo = EventOrganizer.objects.filter(
			user = obj.organizer).first()
		if eo:
			return eo.display_picture
		return None


class NotificationSerializer(serializers.ModelSerializer):
	class Meta:
		models = Notification
		fields = "__all__"

class SongSuggestionSerializer(serializers.ModelSerializer):
	class Meta:
		models = SongSuggestion
		fields = "__all__"

class SearchSerializer(serializers.Serializer):
	term =  serializers.CharField(max_length = 60)