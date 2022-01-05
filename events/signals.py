import os
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete
from .models import Event, SongSuggestion
from .utils import gen_code


@receiver(pre_save, sender=Event)
def add_code(sender, instance, **kwargs):
	if not instance.code or instance.code=="ABCD":
		find_code = True
		while find_code:
			code = gen_code()
			if not Event.objects.filter(code = code).exists():
				instance.code = code
				find_code = False


@receiver(pre_save, sender=SongSuggestion)
def set_playing(sender, instance, **kwargs):
	if instance.is_playing:
		ss = SongSuggestion.objects.filter(event=instance.event, accepted =True, is_playing=True)
		if ss:
			ss.bulk_update(is_playing=False)

@receiver(post_delete, sender=Event)
def auto_delete_file_on_delete(sender, instance, **kwaegs):
	if instance.image and ("party_people_3.png" not in instance.image.path):
		if os.path.isfile(instance.image.path):
			os.remove(instance.image.path)

@receiver(pre_save, sender=Event)
def auto_delete_file_on_change(sender, instance, **kwargs):
	if not instance.pk:
		return False

	try:
		old_file = Event.objects.get(pk = instance.pk).image
	except Event.DoesNotExist:
		return False

	new_file = instance.image
	if new_file and old_file != new_file:
		if os.path.isfile(old_file.path):
			os.remove(old_file.path)

