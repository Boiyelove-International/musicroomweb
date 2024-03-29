import uuid
from datetime import datetime
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from model_utils.models import TimeStampedModel


# Create your models here.
class EventOrganizer(TimeStampedModel):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	display_name = models.CharField(max_length=60)
	profile_photo = models.ImageField(upload_to="profile_photo", null=True, blank=True, default="profile_photo/organizer-profile-icon.png")
	social_profile_photo = models.URLField(null=True, blank=True,)
	devices = models.ManyToManyField('Device', editable=False)



DEVICE_CHOICES = (("android", "Android"),("ios", "IOS"))
class Device(TimeStampedModel):
	device_id = models.CharField(max_length=256)
	fcm_id = models.CharField(max_length=256)
	device_type = models.CharField(max_length=10, default="android")
	device_name = models.CharField(max_length=60, null=True, blank=True)
	show_notification = models.BooleanField(default = True)


	
class PartyGuest(TimeStampedModel):
	user = models.OneToOneField(Device, on_delete=models.CASCADE)
	display_name = display_name = models.CharField(max_length=60)
	profile_photo = models.ImageField(upload_to="profile_photo", null=True, blank=True, default="profile_photo/avatar_upload.png")



VALIDATION_TYPE = (('activation', 'activation'),
	('password_reset', 'password_reset'))


class EmailAddress(TimeStampedModel):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_address', null=True)
	email = models.EmailField(unique=True)
	verified = models.BooleanField(default=False)
	code = models.CharField(max_length=6)
	validation_type = models.CharField(choices = VALIDATION_TYPE, default = VALIDATION_TYPE[0][0], max_length=14 )

	def send_code(self):
		send_mail(
			'Verify Your Email Address',
			'Kindly use this code to activate your account \n code: {0}\n Or visit https://app.musicalroom.co.uk/verify_email/{0}/'.format(self.code),
			settings.DEFAULT_FROM_EMAIL, [self.email,]
			)

	def swap_email(self):
		self.user.email = self.email
		self.user.save()
		self.delete()

class PasswordResetRequest(TimeStampedModel):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	code = models.CharField(max_length=6)
	active = models.BooleanField(default=True)
	used =  models.BooleanField(default=False)

	def send_code(self):
		send_mail(
			'Password Reset',
			'Kindly use this code to reset your password \n code: %s' % self.code,
			settings.DEFAULT_FROM_EMAIL,
			[self.user.email],
			fail_silently=False)


	def send_notice(self):
		send_mail(
			'Your Password Has Been Updated',
			'This is to notify you that your password reset process was successful and your password hyas now been updated \n Thank you',
			settings.DEFAULT_FROM_EMAIL, [self.user.email,]
			)

	def change_password(self, new_password):
		user = self.user
		user.set_password(new_password)
		self.user.save()
		self.used = True
		self.save()


class AccountDeleteRequest(TimeStampedModel):
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	device = models.ManyToManyField(Device)
	party_guest= models.ForeignKey(PartyGuest, on_delete=models.SET_NULL, null=True)
	slug = models.UUIDField(default=uuid.uuid4)
	active = models.BooleanField(default=True)
	confirmed = models.BooleanField(null=True)
	date_completed = models.DateTimeField(null=True)

	def send_deletion_mail(self):
		self.user.is_active = False
		self.user.save()
		send_mail(
			'Confirm Your Account Deletion',
			'A request has been submitted to delete your account.\n Click the link below to confirm your request and delete your account and all associated data. \n Please note that this process is irreverssible. \n code: {0}\n Or visit https://app.musicalroom.co.uk/delete_account/{0}/ '.format(self.slug),
			settings.DEFAULT_FROM_EMAIL, [self.user.email,]
			)

	def delete_user_account(self):
		try:
			eo = EventOrganizer.objects.get(user= self.user)
			for d in eo.devices.all():
				d.delete()
		except:
			pass
		try:
			u = User.objects.get(id = self.user.id)
			u.delete()
			# self.user.delete()
		except:
			pass
		self.date_completed = datetime.now()
		self.active = False
		self.save()

