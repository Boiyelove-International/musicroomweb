import random
import string
from .models import Profile


def generateCode(limit=None):
	if not limit: limit = 6
	return ''.join(random.choices(string.ascii_uppercase + string.digits, k=limit))