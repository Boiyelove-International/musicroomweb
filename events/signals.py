from django.dispatch import receiver
from django.db.models.signals import pre_save
from .models import Event
from .utils import gen_code


@receiver(sender=Event)
def add_code(sender, instance, **kwargs):
	if not instance.code:
		find_code = True
		while find_code:
			code = gen_code()
			if not Event.objects.filter(code = code).exists():
				instance.code = code
				instance.save()
				find_code = False
