from django.dispatch import receiver
from django.db.models.signals import pre_save
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
