from django.db.models import Q
from rest_framework import viewsets, generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from user.permissions import IsLeader
from.serializers import UserSerializer, AuthTokenSerializer, ProjectSerializer,ManageUserSerializer,TaskSerializer
from .models import User, Project, Task
from rest_framework.parsers import MultiPartParser,FormParser


class CreateUserView(generics.CreateAPIView):
    """View for creating user"""
    serializer_class = UserSerializer

class UserLoginApiView(ObtainAuthToken):
    """View for loginning in and token"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = ManageUserSerializer
    parser_classes= [MultiPartParser,FormParser]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrive and return the authenticated user"""
        return self.request.user 

class ProjectViewSet(viewsets.ModelViewSet):
    """Viewset for project"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsLeader]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        """assign the user created the object as the Leader."""
        serializer.save(leader=self.request.user)

    def get_queryset(self):
        """Return projects for the authenticated user as leader or member."""
        user = self.request.user
        return Project.objects.filter(
            Q(leader=user) | Q(members=user)
        ).distinct()


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class=TaskSerializer
    queryset=Task.objects.all()
    def list(self,request,*args, **kwargs):
        email = request.query_params.get('email')
        projectID = request.query_params.get('projectID')
        
        if not email and not projectID:
            return Response({"Detail": "Email or projectID parameter is required"})
        if email and projectID:
            try:
                user=User.objects.get(email=email)
                project=Project.objects.get(id=projectID)
            except User.DoesNotExist or Project.DoesNotExist:
                return Response({"Detail":"User or project not found"})
            tasks=Task.objects.filter(user=user,project=project)
        elif email:
            try:
                user=User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"Detail":"User not found"})
            tasks=Task.objects.filter(user=user)
        elif projectID:
            try:
                project=Project.objects.get(id=projectID)
            except Project.DoesNotExist:
                return Response({"Detail":"Project not found"})
            tasks=Task.objects.filter(project=project)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
