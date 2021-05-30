import traceback

from django.contrib.auth.backends import ModelBackend, AllowAllUsersModelBackend
from rest_framework_simplejwt.authentication import JWTAuthentication

from chat.shared.client import Client
from chat.shared.ldap import Server
from hashlib import sha256

from chat.shared.utils import Certificate_Server


class LDAPBackend(AllowAllUsersModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        certificate = request.data['certificate'].encode()
        cl = Server.ldap_server.find_client(kwargs['login'])
        try:
            Certificate_Server.verify_certificate(certificate)
        except:
            return
        if cl is None:
            return
        if sha256(password.encode('utf-8')).hexdigest() != cl.password.decode():
            return
        cl.certification = certificate
        return cl

# class AuthenticationBackend(JWTAuthentication):
#
#     def get_user(self, validated_token):
#         try:
#             user_id = validated_token[api_settings.USER_ID_CLAIM]
#         except KeyError:
#             raise InvalidToken(_('Token contained no recognizable user identification'))
#
#         try:
#             user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
#         except self.user_model.DoesNotExist:
#             raise AuthenticationFailed(_('User not found'), code='user_not_found')
#
#         if not user.is_active:
#             raise AuthenticationFailed(_('User is inactive'), code='user_inactive')
#
#         return user
