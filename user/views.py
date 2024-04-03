from django.shortcuts import render
from rest_framework import viewsets
from. import serializers
from . import models
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()