from django.core.management.base import BaseCommand, CommandError
from events.utils import create_sample_events

class Command(BaseCommand):
	help = 'Create sample data'


	def  handle(self, *args, **options):
		create_sample_events()
		# self.stdout.write(self.style.SUCCESS('created "%s"' %  st))
		self.stdout.write(self.style.SUCCESS('Successfully created sample data'))