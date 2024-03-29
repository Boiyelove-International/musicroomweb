import pprint
from django.contrib.auth.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView, Response
from accounts.models import EventOrganizer, EmailAddress
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import Device, AccountDeleteRequest
from .apple_oath import AppleOAuth2, verify_apple_auth
from .serializers import UserSerializer, PasswordChangeSerializer, PartyGuestRegistration, ForgotPasswordSerializer


from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def apple_redirect(request):
    post_data = request.POST
    print(post_data)
    query_params = ''
    for key,value in request.POST.items():
        query_params += f'{key}={value}&'

    query_params = query_params[:-1]
    print(query_params)
    response = HttpResponse("", status=302)
    response['Location'] = f'intent://callback?{query_params}#Intent;package={settings.PACKAGE_APP};scheme=signinwithapple;end'
    return response

class OrganizerRegistrationView(APIView):

	#remember to change this
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
		# print("request.data file", request.data.get("file", None))
	
		serializer = PartyGuestRegistration(data=request.data, context={"request": request})
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
		social = request.data.get("social", None)
		# pprint.pprint(request.META)
		# print(" ")
		# pprint.pprint(request.data)
		# print("request.data is", request.data)
		user = None
		eo = None
		display_name = None
		socials = ["facebook", "google", "apple"]

		email = request.data.get("email", None)
		display_name = request.data.get("name", None)
		# print("display name from data is >>>>>>>>>", display_name)
		image_url = request.data.get("image_url", None)
		# print("Request.data is", request.data)

		if social in socials :
			if social == socials[0]:
				#Todo: Verify Facebook
				# 				graph = facebook.GraphAPI(access_token=request.data.get("access_token", None):, version="12.0")
				#  "https://graph.facebook.com/USER-ID?fields=id,name,email,picture&access_token=ACCESS-TOKEN"
				# "access_token" : result.accessToken.token,
				# "id_token" : result.accessToken.userId,
				# "email": profile['email'],
				# "name": profile['first_name']+' '+profile['last_name'],
				# "image_url": profile['picture']['data']['url'],
				pass

			elif social == socials[1]:
				#Todo Verify Google
							# "access_token" : userCredential?.accessToken,
				#   "id_token" : userCredential?.idToken,
				#   "email": data?.email,
				#   "name": data?.displayName,
				#   "image_url": data?.photoUrl,
				pass

			elif social == socials[2]:
				
				# Reuse - Social Login
				if request.data.get("id_token", None) and request.data.get("id_token", None):
					email = verify_apple_auth(
						request.data.get("auth_token", None),
						request.data.get("id_token", None))
				# if email:
					# create User
				# else:
					# Verify Apple
				#Todo Verify Apple
							# "access_token" : userCredential?.accessToken,
				#   "id_token" : userCredential?.idToken,
				#   "email": data?.email,
				#   "name": data?.displayName,
				#   "image_url": data?.photoUrl,


			user = User.objects.filter(email = email.lower())
			if user.exists():
				user = user.first()
			else:
				user = User.objects.create(
					username = email,
					email = email,
					first_name = display_name)
			eo = EventOrganizer.objects.filter(user = user)
			if eo.exists():
				save_eo = False
				eo = EventOrganizer.objects.get(user = user)
				if display_name and not eo.display_name:
					eo.display_name = display_name
					eo.save()
				if image_url and (eo.social_profile_photo != image_url):
					eo.social_profile_photo = image_url
					eo.save()
				if display_name and (display_name != eo.display_name) and display_name != "null null":
					eo.display_name = display_name
					eo.save()

				if not display_name and eo.display_name:
					display_name = eo.display_name
			else:
				eo =EventOrganizer.objects.create(
					user = user ,
					display_name = display_name,
					social_profile_photo = image_url
					)

		if not social:
			serializer = self.serializer_class(
				data = request.data,
				context ={'request': request})
			# print("request.data is", request.data)
			serializer.is_valid(raise_exception=True)
			user = serializer.validated_data['user']
			eo = EventOrganizer.objects.filter(user=user).first()
			display_name = eo.display_name
			fcm_id = request.META.get("HTTP_FCM_DEVICE_ID", None)
			device_id = request.META.get("HTTP_DEVICEID", None)
			device_type = request.META.get("HTTP_DEVICEOS", None)
			device_name = request.META.get("HTTP_DEVICENAME", None)
			if device_id and fcm_id:
				device, created = Device.objects.get_or_create(device_id = device_id)
				device.fcm_id = fcm_id
				device.device_type = device_type
				device.device_name = device_name
				device.save()
				eo.devices.add(device)
		# print("user is", user)
		token, created = Token.objects.get_or_create(user=user)
		

		return Response({
					'token': token.key,
					'email': user.email,
					'display_name': display_name,
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
		pprint.pprint(request.META)
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
			# print("user is", request.auth.user)
			if display_name:
				organizer = EventOrganizer.objects.get(user = request.auth.user)
				organizer.display_name = display_name
				organizer.save()
				return Response(
					{
					'display_name': display_name,
					},
					status=status.HTTP_200_OK)
			# print('errors are ', serializer.errors)
			errors.update(serializer.errors)



		elif action_type == 'verify_email':
			email = request.data.get('email')
			code = request.data.get('code')
			try: 
				email_ver = EmailAddress.objects.get(user=request.auth.user, email=email, code=code)
				email_ver.swap_email()
				# print(request.user)
				# print(request.auth.user)
				# print(request.auth.user.refresh_from_db)
				return Response({'email': request.auth.user.email}, status=status.HTTP_200_OK)
			except EmailAddress.DoesNotExist:
				errors.update({'error': 'invalid code'})


		elif action_type == 'resend_code':
			request.data.get('email')
			if EmailAddress.objects.filter(email=email, user=request.auth.user).exists():
				email_ver = EmailAddress.objects.get(email=email, user=request.auth.user)
				email_ver.send_code()

		elif action_type == "delete_account":
			password = request.data.get("password")
			print("password is =======>", password)
			if (request.auth.user.check_password(password)):
				AccountDeleteRequest.objects.create(
					user = request.auth.user)
				return Response(
					{"detail": "Account Deletion Initiated"},
					status=status.HTTP_200_OK)
			else:

				errors.update({'error': 'invalid password'})

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
		pprint.pprint(self.request.data)
		pprint.pprint(request.data)
		pprint.pprint(kwargs)
		action_type = kwargs.get('step', "send_code")
		serializer = ForgotPasswordSerializer(data = request.data)
		# serializer.is_valid(raise_exception=True)
		# pprint.pprint(serializer.data)
		# pprint.pprint(serializer.errors)
		if serializer.is_valid(raise_exception=True):
			if action_type == "send_code":
				serializer.create()
				return Response({"detail": "Foorgot password email sent"}, status = status.HTTP_201_CREATED)
			if action_type == "verify_code":
				return Response({"detail": "You can now update your password"}, status=status.HTTP_200_OK)
			if action_type == "change_password":
				serializer.changePassword()
				return Response({"detail": "Password Updated Successfully"}, status=status.HTTP_200_OK)
			
		print("running this error")
		return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


