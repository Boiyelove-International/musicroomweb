import jwt
import requests
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from social_core.backends.oauth import BaseOAuth2
from social_core.utils import handle_http_errors



def verify_apple_auth(access_token, id_token):
    kwargs = {}
    email = None
    name = 'apple'
    ACCESS_TOKEN_URL = 'https://appleid.apple.com/auth/token'
    SCOPE_SEPARATOR = ','
    ID_KEY = 'uid'


    """
    Finish the auth process once the access_token was retrieved
    Get the email from ID token received from apple
    """
    response_data = {}
    headers = {
        'kid': settings.SOCIAL_AUTH_APPLE_KEY_ID
    }


    payload = {
        'iss': settings.SOCIAL_AUTH_APPLE_TEAM_ID,
        'iat': timezone.now(),
        'exp': timezone.now() + timedelta(days=180),
        'aud': 'https://appleid.apple.com',
        'sub': settings.SOCIAL_AUTH_APPLE_CLIENT_ID,
    }

    client_secret = jwt.encode(
        payload, 
        settings.SOCIAL_AUTH_APPLE_ID_SECRET, 
        algorithm='ES256', 
        headers=headers
    )
    # decoded = jwt.decode("01535.bdc7a13a717d4db08a30061764990ffd.1753", audience='https://appleid.apple.com', options={"verify_signature": False})
    try:
        client_secret = client_secret.decode()
        print("client_secret =>>>>>>>>>", client_secret.decode())
    except:
        pass


    # Step 2
    headers = {'content-type': "application/x-www-form-urlencoded"}
    data = {
        'client_id': settings.SOCIAL_AUTH_APPLE_CLIENT_ID,
        'client_secret': client_secret,
        'code': access_token,
        'grant_type': 'authorization_code',
    }

    if id_token:
        decoded_id_token = jwt.decode(id_token, settings.SOCIAL_AUTH_APPLE_ID_SECRET, audience="uk.co.musicalroom.musicalroom", algorithms=['ES256'], options={"verify_signature": False})
        print("decoded id_token is >>>>>>>>>>>", decoded_id_token)
        email = decoded_id_token.get("email", None)

    return email
    res = requests.post(ACCESS_TOKEN_URL, data=data, headers=headers)
    response_dict = res.json()
    print("response dict is >>>>>>>>>>>", response_dict)

    id_token_received = response_dict.get('id_token', None)

    # if id_token != id_token_received: return None

    if id_token_received:
        decoded = jwt.decode(id_token_received, settings.SOCIAL_AUTH_APPLE_ID_SECRET, audience="uk.co.musicalroom.musicalroom", algorithms=['ES256'], options={"verify_signature": False})
        response_data.update({'email': decoded['email']}) if 'email' in decoded else None
        response_data.update({'uid': decoded['sub']}) if 'sub' in decoded else None
        email = decoded.get("email", None)

    return email





class AppleOAuth2(BaseOAuth2):
    """apple authentication backend"""

    name = 'apple'
    ACCESS_TOKEN_URL = 'https://appleid.apple.com/auth/token'
    SCOPE_SEPARATOR = ','
    ID_KEY = 'uid'

    @handle_http_errors
    def do_auth(self, access_token, *args, **kwargs):
        """
        Finish the auth process once the access_token was retrieved
        Get the email from ID token received from apple
        """
        response_data = {}
        client_id, client_secret = self.get_key_and_secret()

        headers = {'content-type': "application/x-www-form-urlencoded"}
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': access_token,
            'grant_type': 'authorization_code',
        }

        res = requests.post(ACCESS_TOKEN_URL, data=data, headers=headers)
        response_dict = res.json()
        id_token = response_dict.get('id_token', None)

        if id_token:
            print("code entered here")
            decoded = jwt.decode(id_token, settings.SOCIAL_AUTH_APPLE_ID_SECRET, audience="uk.co.musicalroom.musicalroom", algorithms=['ES256'], options={"verify_signature": False})
            response_data.update({'email': decoded['email']}) if 'email' in decoded else None
            response_data.update({'uid': decoded['sub']}) if 'sub' in decoded else None

        response = kwargs.get('response') or {}
        response.update(response_data)
        response.update({'access_token': access_token}) if 'access_token' not in response else None

        kwargs.update({'response': response, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)

 
    def get_user_details(response):
        email = response.get('email', None)
        details = {
            'email': email,
        }
        return details

    @staticmethod
    def get_key_and_secret():
        headers = {
            'kid': settings.SOCIAL_AUTH_APPLE_KEY_ID
        }

        payload = {
            'iss': settings.SOCIAL_AUTH_APPLE_TEAM_ID,
            'iat': timezone.now(),
            'exp': timezone.now() + timedelta(days=180),
            'aud': 'https://appleid.apple.com',
            'sub': settings.SOCIAL_AUTH_APPLE_CLIENT_ID,
        }

        client_secret = jwt.encode(
            payload, 
            settings.SOCIAL_AUTH_APPLE_ID_SECRET, 
            algorithm='ES256', 
            headers=headers
        )
        print("client_secret =>>>>>>>>>", client_secret)
        try:
            print("client_secret =>>>>>>>>>", client_secret.decode())
        except:
            pass
        
        return settings.SOCIAL_AUTH_APPLE_CLIENT_ID, client_secret