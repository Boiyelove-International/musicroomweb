from django.urls import path
from .viewsets import GuestRegistrationView, OrganizerRegistrationView, CustomAuthToken, EmailVerificationView, ForgotPassword, UserDetailView
# , UserDetailView, ForgotPassword, EmailVerificationView


urlpatterns = [
	# path('user/', UserRecordView.as_view(), name='users-api'),
	path('login/', CustomAuthToken.as_view(), name='login-user'),
	path('register/guest/', GuestRegistrationView.as_view(), name='register-guest'),
	path('register/', OrganizerRegistrationView.as_view(), name='register-organizer'),
	path('verify_email/',EmailVerificationView.as_view(), name='verify-email'),
	path('forgot-password/<slug:step>/', ForgotPassword.as_view(), name='forgot-password'),
	path('account-settings/<slug:action_type>/', UserDetailView.as_view(), name='update-user-detail'),
	# path('oauth/', include('rest_framework_social_oauth2.urls')),
    # path('oauth/apple/', views.apple_redirect),
	]
