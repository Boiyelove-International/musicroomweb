from django.urls import path
from django.conf import settings
from . import viewsets


urlpatterns = [
	path('events/', viewsets.EventCreateView.as_view(), name='events-list-create'),
	path('event/join/', viewsets.JoinEventView.as_view(), name='join-event'),
	
	path('event/<int:pk>/', viewsets.EventDetailView.as_view(), name='events-detail-update-delete'),
	path('event/<int:pk>/suggestions/', viewsets.EventDetailView.as_view(), name='events-suggestions'),
	path('suggestions/', viewsets.SuggestionListView.as_view(), name='suggestions'),
	path('notifications/', viewsets.NotificationListView.as_view(), name='notifications'),
	path('search/', viewsets.SearchSongView.as_view(), name='search'),
	]
