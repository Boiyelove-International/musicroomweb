from django.urls import path
from django.conf import settings
from . import viewsets

urlpatterns = [
	path('events/', viewsets.EventCreateView.as_view(), name='events'),
	path('events/<int:pk>/', viewsets.EventCreateView.as_view(), name='events'),
	path('events/join/', viewsets.JoinEventView.as_view(), name='join-event'),
	path('suggestions/', viewsets.SuggestionUpdate.as_view(), name='suggestions'),
	path('notifications/', viewsets.NotificationListView.as_view(), name='notifications'),
	path('search/', viewsets.SearchSongView.as_view(), name='search'),
	]
