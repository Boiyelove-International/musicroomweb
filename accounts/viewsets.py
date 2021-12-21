from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView, Response
from accounts.models import EventOrganizer, EmailAddress
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .serializers import UserSerializer, PasswordChangeSerializer, PartyGuestRegistration



class OrganizerRegistrationView(APIView):

	#remeber to change this
	# permission_classes = [IsAdminUser]

	# def get(self, format=None):
	# 	users = UserObjects.all()
	# 	serializer = UserSerializer(users, many=True)
	# 	return Response(serializer.data)



	def post(self, request):
		request.data["username"] =  request.data.get('email', None)
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			serializer.create(validated_data=request.data)
			return Response(
				serializer.data,
				status = status.HTTP_201_CREATED
				)
		return Response(
			{
				"error": True,
				"errors": serializer.errors,

			},
			status= status.HTTP_400_BAD_REQUEST
			)


class GuestRegistrationView(APIView):
	# permission_classes = [AllowAny]

	def post(self, request):
		file = request.data.get("file", None)
		profile_photo = request.data.get("profile_photo", None)
		print("request.data file", request.data.get("file", None))
		serializer = PartyGuestRegistration(data=request.data)
		serializer.is_valid(raise_exception = True)
		serializer.create()
		return Response(
					serializer.validated_data,
					status = status.HTTP_201_CREATED
					)	

class PartyGuestProfile(APIView):
	def post(self, request):
		display_name = request.data.get("display_name", None)
		guest_id = request.META.get("HTTP_GUEST")
		if guest_id and display_name:
			device = Device.objects.filter(
				device_id = guest_id
				).first()
			if device:
				pg = PartyGuest.objects.filter(user = device).first()
				pg.display_name = display_name
				pg.dave()
				return Response(
					{"dusplay_name": display_name},
					status = status.HTTP_200_OK
					)
		return Response(
					{"detail": "Provide display name"},
					status = status.HTTP_400_BAD_REQUEST
					)	


class CustomAuthToken(ObtainAuthToken):

	def post(self, request, *args, **kwargs):
		serializer = self.serializer_class(
			data = request.data,
			context ={'request': request})
		print("request.data is", request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data['user']
		print("user is", user)
		token, created = Token.objects.get_or_create(user=user)
		obj = EventOrganizer.objects.filter(user=user).first()


		return Response({
					'token': token.key,
					'email': user.email,
					'display_name': obj.display_name,
					})


class UserDetailView(APIView):
	#add object level permission only user can access thier details or admin
	permission_class = [IsAuthenticated]

	def get_object(self, pk):
		try:
			return User.objects.get(pk=pk)
		except User.DoesNotExist:
			raise Http404

	def post(self, request, action_type=None, format=None):

		errors = {}
		if action_type == 'change_password':
			serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
			if serializer.is_valid():
				serializer.change_password()
				return Response(
					{"detail": "Password updated"},
					status=status.HTTP_200_OK)
			errors.update(serializer.errors)

		elif action_type == 'change_email':
			# serializer = EmailValidationSerializer(data=request.data, context={'request': request})
			# if serializer.is_valid():
			# 	serializer.create()
			email = request.data.get("email")
			if email:
				user = request.auth.user
				user.email = email
				user.save()
				return Response(
					{"email": email},
					status=status.HTTP_200_OK)
			errors.update(serializer.errors)

		elif action_type == 'change_name':
			display_name = request.data.get("display_name")
			print("user is", request.auth.user)
			if display_name:
				organizer = EventOrganizer.objects.get(user = request.auth.user)
				organizer.display_name = display_name
				organizer.save()
				return Response(
					{
					'display_name': display_name,
					},
					status=status.HTTP_200_OK)
			print('errors are ', serializer.errors)
			errors.update(serializer.errors)


		elif action_type == 'verify_email':
			email = request.data.get('email')
			code = request.data.get('code')
			try: 
				email_ver = EmailAddress.objects.get(user=request.auth.user, email=email, code=code)
				email_ver.swap_email()
				print(request.user)
				print(request.auth.user)
				print(request.auth.user.refresh_from_db)
				return Response({'email': request.auth.user.email}, status=status.HTTP_200_OK)
			except EmailAddress.DoesNotExist:
				errors.update({'error': 'invalid code'})


		elif action_type == 'resend_code':
			request.data.get('email')
			if EmailAddress.objects.filter(email=email, user=request.auth.user).exists():
				email_ver = EmailAddress.objects.get(email=email, user=request.auth.user)
				email_ver.send_code()


		return Response(errors, status=status.HTTP_400_BAD_REQUEST)

class EmailVerificationView(APIView):
	def post(self, request, *args, **kwargs):
		serializer = EmailVerificationSerializer(data=request.data)
		if serializer.is_valid():
			serializer.verify()
			return Response(status = status.HTTP_200_OK)
		return Response(
			serializer.errors,
			status= status.HTTP_400_BAD_REQUEST
			)	



class ForgotPassword(APIView):

	def post(self, request, *args, **kwargs):
		action_type = kwargs.get('step', "send_code")
		serializer = ForgotPasswordSerializer(data = request.data)
		if serializer.is_valid():
			if action_type == "send_code":
				serializer.create()
				return Response(status = status.HTTP_201_CREATED)
			if action_type == "verify_code":
				pass
			if action_type == "change_password":
				serializer.changePassword()
			return Response(status=status.HTTP_200_OK)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)