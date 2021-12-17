from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Event, SongSuggestion, Notification


class EventSerializer(models.ModelSerializer):
	class Meta:
		model = Event
		fields = "__all__"

class NotificationSerializer(models.ModelSerializer):
	class Meta:
		models = Notification
		fields = "__all__"

class SongSuggestion(models.ModelSerializer):
	class Meta:
		models = SongSuggestion
		fields = "__all__"