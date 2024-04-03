from rest_framework import serializers
from . import models

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.User
        fields=['email','name','password']
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
