from django.urls import path, include
from . import urls_api
from . import views

app_name = 'events'
urlpatterns = [
	path('api/', include(urls_api)),
	]
