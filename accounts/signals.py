from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token



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
def create_profile(sender, instance, created, *args, **kwargs):
	if created:
		Token.objects.create(user=instance)