from rest_framework import viewsets, generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from.serializers import UserSerializer, AuthTokenSerializer
from .models import User
from . import permissions


class CreateUserView(generics.CreateAPIView):
    """View for creating user"""
    serializer_class = UserSerializer


class UserLoginApiView(ObtainAuthToken):
    """View for loginning in and token"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ProjectViewSet():
    """"""
