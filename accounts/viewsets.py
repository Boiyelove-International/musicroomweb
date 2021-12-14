from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView, Response
from accounts.models import EventOrganizer, EmailAddress
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import UserSerializer



class UserRecordView(APIView):

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
				return Response(status=status.HTTP_200_OK)
			errors.update(serializer.errors)

		elif action_type == 'change_email':
			serializer = EmailValidationSerializer(data=request.data, context={'request': request})
			if serializer.is_valid():
				serializer.create()
				return Response(status=status.HTTP_200_OK)
			errors.update(serializer.errors)

		elif action_type == 'change_name':
			serializer = UserProfileSerializer(data=request.data, context={'request': request})
			if serializer.is_valid(raise_exception = True):
				serializer.save()
				return Response(
					{'email': request.auth.user.email,
					'first_name': request.auth.user.first_name,
					'last_name': request.auth.user.last_name,
					'phone_number': request.auth.user.profile.phone_number},
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
				return Response(status = status.HTTP_200_OK)

		elif action_type == 'change_card':
			card_id = int(request.data.get('card_id'))
			card = PaymentCard.objects.get(id=card_id, user=request.auth.user)
			card.default = True,
			card.save()
			return Response(status = status.HTTP_200_OK)

		elif action_type == 'remove_card':
			card_id = int(request.data.get('card_id'))
			card = PaymentCard.objects.get(id=card_id, user=request.auth.user)
			card.delete()
			return Response(status = status.HTTP_200_OK)

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