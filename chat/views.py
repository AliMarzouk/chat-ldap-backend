from hashlib import sha256

from django.shortcuts import render

from rest_framework import generics
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView

from chat.models import Snippet, User
from chat.serializers import SnippetSerializer, CustomObtainPairSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

from chat.shared.client import Client
from chat.shared.ldap import Server

def index(request):
    return render(request, 'chat/index.html')


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })


class CustomTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = CustomObtainPairSerializer


class SnippetList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def perform_create(self, serializer):
        data = self.request.data
        hashed = sha256(data['password'].encode('utf-8')).hexdigest()
        cl = Client(data['num'], data['nom'], data['prenom'], data['login'], hashed, 'certification')
        Server.ldap_server.create(cl)
        serializer.save()

