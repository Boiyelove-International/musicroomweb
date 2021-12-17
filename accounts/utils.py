import random
import string
from .models import Profile
from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context


def generateCode(limit=None):
	if not limit: limit = 6
	return ''.join(random.choices(string.ascii_uppercase + string.digits, k=limit))



def send_cute_mail(template, subject, data, from_email, to):
	plaintext = get_template("/emails/" + template + '.txt')
	htmly     = get_template("/emails/" + template + '.html')
	d = Context(data)
	# subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
	text_content = plaintext.render(d)
	html_content = htmly.render(d)
	msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
	msg.attach_alternative(html_content, "text/html")
	msg.send()