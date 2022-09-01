import re
import pprint
import json
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator,UniqueValidator
from .models import EventOrganizer, EmailAddress, PasswordResetRequest, Device, PartyGuest



class UserSerializer(serializers.ModelSerializer):
	display_name = serializers.CharField(max_length=30)

	def create(self, validated_data):
		validated_data["first_name"] = validated_data.pop("display_name")
		user = User.objects.create_user(**validated_data)
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
				),
			]

	def validate_password(self, value):
		password_validation.validate_password(value, self.instance)
		passCheck = re.compile("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$")
		if passCheck.fullmatch(value):
			return value
		raise serializers.ValidationError("Choose a stronger password. Your password must be a minium of 8 characters. Also, it must contain at least 1 Uppercase (A-Z), 1 lowercase (a-z), 1 Number (0-9) and 1 Special character (#?!@$%^&*-)")

	def validate(self, data):
		xdata = data.copy()
		data.pop("display_name", None)
		user = User(**data)
		password = data.get("password")
		errors = dict()
		try:
			password_validation.validate_password(password=password, user=user)
		except exceptions.ValidationError as e:
			errors['password'] = list(e.messages)

		if errors:
			raise serializers.ValidationError(errors)

		return super(UserSerializer, self).validate(xdata)

	def validate_email(self, value):
		if not User.objects.filter(email = value.strip()).exists():
			return value
		raise serializers.ValidationError('Account already exists')

	def validate_username(self, value):
		# print("entered username validation state")
		if not User.objects.filter(username = value.strip()).exists():
			return value
		raise serializers.ValidationError('Account already exists')


class NotificationsSerializer(serializers.ModelSerializer):
	class Meta:
		fields = ["content"]



class EmailValidationSerializer(serializers.ModelSerializer):
	class Meta:
		model = EmailAddress
		fields = ('email',)


	def validate_email(self, value):
		user = self.get_user()
		if EmailAddress.objects.filter(email = user.email, validation_type='activation', verified=False).exists():
			raise serializers.ValidationError('Please verify your default email address to continue')

		if  User.objects.filter(email = value).exists() or EmailAddress.objects.filter(email = value).exists():
			raise serializers.ValidationError('Email already registered')
		return value

	def get_user(self):
		request = self.context.get('request')
		if request and hasattr(request, 'auth'):
			return request.auth.user
		raise serializers.ValidationError("account not found")

	def create(self):
		email_ver, created = EmailAddress.objects.get_or_create(
			user= self.get_user(), email= self.validated_data['email'])
		return email_ver


class PasswordChangeSerializer(serializers.Serializer):
	old_password = serializers.CharField(min_length=8)
	new_password = serializers.CharField(min_length=8)


	def validate_old_password(self, value):
		user = self.get_user()
		if not user.check_password(value):
			raise serializers.ValidationError("password is incorrect")
		return value
		

	def get_user(self):
		request = self.context.get('request')
		if request and hasattr(request, 'auth'):
			return request.auth.user
		raise serializers.ValidationError("account not found")


	def change_password(self):
		user = self.get_user()
		user.set_password((self.validated_data['new_password']).strip())
		user.save()



class ForgotPasswordSerializer(serializers.Serializer):
	email =  serializers.EmailField()
	code = serializers.CharField(required = False)
	new_password = serializers.CharField(required = False)

	def validate_email(self, value):
		if not User.objects.filter(email=value).exists():
			raise serializers.ValidationError("User with email address does not exist")
		return value

	def get_user(self):
		email = self.initial_data.get("email")
		return User.objects.get(email = email)

	def validate_code(self, value):
		if value:
			print("value is ", value)
			if not PasswordResetRequest.objects.filter(user = self.get_user(),
			code = value, active= True).exists():
				print("user is", self.get_user())
				pr = PasswordResetRequest.objects.get(
			code = value.strip().upper())
				print("RAISING INVALID CODE")
				raise serializers.ValidationError("Invalid code")
		return value


	def changePassword(self):
		user = self.get_user()
		password = self.validated_data.get('new_password')
		if not password: raise serializers.ValidationError("New password is required")
		user.set_password(password)
		user.save()
		prr = PasswordResetRequest.objects.get(
			user=user,
			code = self.validated_data.get('code'),
			active = True)
		prr.used = True
		prr.active =False	
		prr.save()
		prr.send_notice()

	def create(self):
		PasswordResetRequest.objects.create(user=self.get_user())


class PartyGuestRegistration(serializers.Serializer):
	device_id = serializers.CharField(max_length=100)
	display_name = serializers.CharField(max_length=60)

	def create(self):
		device, created = Device.objects.get_or_create(
			device_id = self.validated_data["device_id"],
		# device_name =self.validated_data["device_name"]
			)
		request = self.context.get('request')
		fcm_id = request.META.get("HTTP_FCM_DEVICE_ID", None)
		device_type = request.META.get("HTTP_DEVICEOS", None)
		device_name = request.META.get("HTTP_DEVICENAME", None)
		if fcm_id:
			device.fcm_id = fcm_id
			device.device_type = device_type
			device.device_name = device_name
			device.save()
		try:
			pg = PartyGuest.objects.get(
			user = device,
			)
			pg.display_name = self.validated_data["display_name"]
			pg.save()
		except PartyGuest.DoesNotExist:
			PartyGuest.objects.create(
			user = device,
			display_name = self.validated_data["display_name"])


class PartyGuestSerializer(serializers.ModelSerializer):
	class Meta:
		model = PartyGuest
		fields = ("display_name", "profile_photo",)


