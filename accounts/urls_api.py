from django.urls import path
from .viewsets import UserRecordView, CustomAuthToken, EmailVerificationView, ForgotPassword, UserDetailView
# , UserDetailView, ForgotPassword, EmailVerificationView


urlpatterns = [
	# path('user/', UserRecordView.as_view(), name='users-api'),
	path('login/', CustomAuthToken.as_view(), name='login-user'),
	path('register/', UserRecordView.as_view(), name='register-users'),
	path('verify_email/',EmailVerificationView.as_view(), name='verify-email'),
	path('forgot-password/<slug:step>/', ForgotPassword.as_view(), name='forgot-password'),
	path('account-settings/<slug:action_type>/', UserDetailView.as_view(), name='update-user-detail'),
	]
