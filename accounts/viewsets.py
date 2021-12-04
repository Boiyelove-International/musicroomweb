from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView, Response
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
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data['user']
		token, created = Token.objects.get_or_create(user=user)
		try:
			obj, created = EventOrganizer.objects.get_or_create(user=user)
		except:
			phone_number = None

		return Response({
					'token': token.key,
					'email': user.email,
					'display_name': user.first_name,
					})