from rest_framework import serializers
from . import models
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.User
        fields=['id','email','name','password']
        extra_kwargs={
            'password':{
                'write_only':True,
                'style':{
                    'input_type':'password'
                }
            }
        }
    def create(self, validated_data):
        user = models.User.objects.create_user(**validated_data)
        return user
    def update(self,instance,validated_data):
        if 'password' in validated_data:
            password= validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance,validated_data)

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = ('Unable to authenticate with these credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class ProjectSerializer(serializers.ModelSerializer):
    # memebers by email
    # in get or retrieve only for related user
    leader = UserSerializer(required = False)
    class Meta:
        model = models.Project
        fields = ['id', "name", "description", "leader", "deadline", "memebers", "created"]

    def create(self, validated_data):
            # Set the 'leader' field to the current authenticated user
            validated_data['leader'] = self.context['request'].user
            project = models.Project.objects.create(**validated_data)
            return project

