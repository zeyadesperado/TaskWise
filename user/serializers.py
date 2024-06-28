from rest_framework import serializers
from .models import User, Project, Task,Comment
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
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
        user = User.objects.create_user(**validated_data)
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

class CommentSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model=Comment
        fields = ['id', 'text', 'user', 'project', 'created']
        read_only_fields=['user','created']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model=Task
        fields = ['id','name','description','project','finished','deadline','user']
    def update(self, instance, validated_data):
        validated_data.pop('user', None)  # Prevent 'user' from being updated
        validated_data.pop('project', None)  # Prevent 'project' from being updated
        return super().update(instance, validated_data)
    

class ManageUserSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True,read_only=True)
    class Meta:
        model=User
        fields=['id','email','name','password','resume_file','tasks']
        extra_kwargs={
            'password':{
                'write_only':True,
                'style':{
                    'input_type':'password'
                }
            }
        }
    def update(self,instance,validated_data):
        if 'password' in validated_data:
            password= validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance,validated_data)

class ProjectSerializer(serializers.ModelSerializer):
    leader = UserSerializer(read_only=True)
    members = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True,
        required=False
    )
    members_detail = UserSerializer(source='members', many=True, read_only=True)
    deadline = serializers.DateTimeField(format='%d/%m/%Y %H:%M', required=False)
    created = serializers.DateTimeField(format='%d/%m/%Y %H:%M', required=False)
    comments = CommentSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True,read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'leader', 'deadline', 'members', 'members_detail', 'created','comments','tasks']
        read_only_fields = ['leader']

    def create(self, validated_data):
        members_emails = validated_data.pop('members', [])
        project = Project.objects.create(**validated_data)
        members = []
        for email in members_emails:
            try:
                user = User.objects.get(email=email)
                members.append(user)
            except User.DoesNotExist:
                raise serializers.ValidationError(f"User with email '{email}' does not exist.")
        project.members.set(members)
        return project

    def update(self, instance, validated_data):
        members_emails = validated_data.pop('members', None)
        if members_emails is not None:
            members = []
            for email in members_emails:
                try:
                    user = User.objects.get(email=email)
                    members.append(user)
                except User.DoesNotExist:
                    raise serializers.ValidationError(f"User with email '{email}' does not exist.")
            instance.members.set(members)
            instance.save()
            return instance
        return super().update(instance, validated_data)




