from django.db.models import Q
from rest_framework import viewsets, generics,status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from user.permissions import IsLeader, IsCommentOwnerOrleader,IsTaskOwnerOrLeader
from.serializers import UserSerializer, AuthTokenSerializer, ProjectSerializer,ManageUserSerializer,TaskSerializer,CommentSerializer
from .models import User, Project, Task, Comment
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
        user = self.request.user
        return User.objects.prefetch_related('tasks').get(pk=user.pk)

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
        ).distinct().prefetch_related('comments').prefetch_related('tasks')


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class=TaskSerializer
    queryset=Task.objects.all()
    permission_classes = [IsAuthenticated, IsTaskOwnerOrLeader]
    authentication_classes = [TokenAuthentication]
    def create(self, request, *args, **kwargs):
        # Ensure only the project leader can create a task
        project_id = request.data.get('project')
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Project does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the requester is the project leader
        if project.leader != request.user:
            return Response({"detail": "Only the project leader can create tasks for this project."},
                            status=status.HTTP_403_FORBIDDEN)
        
        #check if the user is a member or a leader of the project
        assigned_user_id = request.data.get('user')
        try:
            assigned_user = User.objects.get(pk=assigned_user_id)
        except User.DoesNotExist:
            return Response({"detail": "Assigned user does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if assigned_user not in project.members.all() and assigned_user != project.leader:
            return Response({"detail": "The assigned user must be a member of the project."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
    def get_queryset(self):
        user = self.request.user
        if self.action == 'list':
            return Task.objects.filter(user=user).distinct()    
        return Task.objects.filter(Q(user=user) | Q(project__leader=user)).distinct()


class CommentViewset(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated,IsCommentOwnerOrleader]
    authentication_classes = [TokenAuthentication]
    def perform_create(self,serializer):
        print("Headers: ", self.request.headers)
        """save the user with the authenticated user"""
        serializer.save(user=self.request.user)
    



