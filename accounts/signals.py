from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import EmailAddress, PasswordResetRequest, EventOrganizer, AccountDeleteRequest
from .utils import generateCode


#signals
@receiver(pre_save, sender=User)
def setLowercaseValues(sender, instance, *args, **kwargs):
	# instance.active = False
	if instance.username and not instance.email and '@' in instance.username:
		instance.username = instance.username.lower()
		instance.email = instance.username

	instance.email = instance.email.lower()
	instance.username = instance.email


@receiver(post_save, sender=User)
def create_token(sender, instance, created, *args, **kwargs):
	if created:
		Token.objects.create(user=instance)
		if not EventOrganizer.objects.filter(user=instance).exists():
			EventOrganizer.objects.create(user=instance, display_name = instance.first_name)



@receiver(pre_save, sender=EmailAddress)
@receiver(pre_save, sender=PasswordResetRequest)
def addVerificationCode(sender, instance, *args, **kwargs):
	code  = generateCode()
	if sender == PasswordResetRequest:
		while PasswordResetRequest.objects.filter(user = instance.user, code = code).exists():
			code  = generateCode()
		# if instance.id or instance.pk:
		# 	PasswordResetRequest.objects.filter(user = instance.user, active=True).update(active = False)
	instance.code = code

@receiver(post_save, sender=EmailAddress)
@receiver(post_save, sender=PasswordResetRequest)
def sendPassWordResetCode(sender, instance, created, *args, **kwargs):
	# if user is inactive, dont request reset password
	# if user is active (email verified), 
	if created:
		instance.send_code()
		# upon saving a new request, disable all previous requests
		if sender == PasswordResetRequest:
			other_requests = PasswordResetRequest.objects.filter(user=instance.user, active=True).exclude(id=instance.id)
			other_requests.update(active=False)


@receiver(post_save, sender=AccountDeleteRequest)
def send_mail(sender, instance, created, *args, **kwargs):
	if created:
		instance.send_deletion_mail()