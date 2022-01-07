from django.db import models
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
			'Kindly use this code to activate your account \n code: {0}\n Or visit https://app.verifyproperty.online/verify_email/{0}/'.format(self.code),
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

