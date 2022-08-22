from django.urls import path, include
from . import urls_api
from . import views

app_name = 'accounts'
urlpatterns = [
	path("delete_account/<slug:slug>/", views.AccountDeleteView.as_view()),
	path('api/', include(urls_api)),

	]



