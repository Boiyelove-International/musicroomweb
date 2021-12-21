from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import EventOrganizer, EmailAddress, PasswordResetRequest, Device, PartyGuest



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
			raise serializer.ValidationError('Please verify your default email address to continue')

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
		if value and not PasswordResetRequest.objects.filter(user = self.get_user(),
			code = value,
			active= True).exists():
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

		


