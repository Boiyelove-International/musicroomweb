from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Event, SongSuggestion, Notification


class EventSerializer(serializers.ModelSerializer):
	class Meta:
		model = Event
		fields = "__all__"

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