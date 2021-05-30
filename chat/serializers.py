
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from chat.models import Snippet, User


class SnippetSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Snippet
        fields = ['id', 'title', 'code', 'linenos', 'language', 'style', 'owner']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['login', 'password', 'nom', 'prenom', 'num', 'certification']


class CustomObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(CustomObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['username'] = user.login
        token['user_certificate'] = user.certification.decode()
        return token
