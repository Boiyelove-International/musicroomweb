from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import EventOrganizer


class UserSerializer(serializers.ModelSerializer):
	display_name = serializers.CharField(max_length=30)

	def create(self, validated_data):
		display_name = validated_data.pop("display_name")
		user = User.objects.create_user(**validated_data)
		EventOrganizer.objects.create(display_name = display_name, user=user)
		return user

	class Meta:
		model = User
		fields = (
			'email',
			'username',
			'password',
			"display_name"
			)
		validators = [
			UniqueTogetherValidator(
				queryset=User.objects.all(),
				fields = ['username', 'email']
				)
			]