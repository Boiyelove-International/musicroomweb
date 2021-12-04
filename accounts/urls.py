from django.urls import path, include
from . import urls_api
from . import views

app_name = 'accounts'
urlpatterns = [
	# path('login/', views.LoginView.as_view(), name='login'),
	# path('logout/', views.logout, name='web-logout'),
	
	# path('register/', views.RegisterView.as_view(), name='register'),
	# path('user/', views.UserDetailView.as_view()),
	# path('verify_email/<slug:code>/',views.EmailVerificationView.as_view()),
	# path('forgot-password/', views.ForgotPasswordView.as_view(), name='reset-password'),
	# path('forgot-password/<slug:code>/', views.ForgotPasswordView.as_view(), name='reset-password-confirm'),

	# path('update_password/', views.PasswordChangeFormView.as_view(), name='update-password'),
	# path('profile-settings/', views.UserDetailView.as_view(), name='web-account-settings'),
	# path('change_email/', views.EmailUpdateView.as_view(), name='web-update-email'),

	# path('change-card/', views.UserDetailView.as_view()),
	path('api/', include(urls_api)),

	]



