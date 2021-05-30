from hashlib import sha256

from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from chat.models import Snippet, User
from chat.serializers import SnippetSerializer, CustomObtainPairSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

from chat.shared.client import Client
from chat.shared.ldap import Server
from chat.shared.utils import Certificate_Server


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
        certificate = Certificate_Server.generate_certificate(data['cert_req'].encode())
        hashed = sha256(data['password'].encode('utf-8')).hexdigest()
        cl = Client(data['num'], data['nom'], data['prenom'], data['login'], hashed, certificate)
        self.client = cl
        Server.ldap_server.create(cl)
        serializer.save(username=data['login'])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'certificate': self.client.certification}, status=status.HTTP_201_CREATED, headers=headers)

