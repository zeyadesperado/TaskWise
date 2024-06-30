from django.db.models import Q
from rest_framework import viewsets, generics,status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from user.permissions import IsLeader, IsCommentOwnerOrleader,IsTaskOwnerOrLeader
from .serializers import UserSerializer, AuthTokenSerializer, ProjectSerializer,ManageUserSerializer,TaskSerializer,CommentSerializer, ToDoListSerializer, ToDoItemSerializer,UserViewOnlySerializer
from .models import User, Project, Task, Comment, ToDoItem, ToDoList
from rest_framework.parsers import MultiPartParser,FormParser
from user.task_recommendation import process_resumes_and_task
import google.generativeai as genai
import os

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
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
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

        # Set the user field for the task explicitly
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save(user=assigned_user,project=project)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # print("******************************") #testing line 1
        # self.perform_create(serializer)
        # print("------------------------------") #testing line 2
        # headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
        """save the user with the authenticated user"""
        serializer.save(user=self.request.user)

class ToDoListViewSet(viewsets.ModelViewSet):
    queryset = ToDoList.objects.all()
    serializer_class = ToDoListSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return ToDoList.objects.filter(owner=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ToDoItemViewSet(viewsets.ModelViewSet):
    queryset = ToDoItem.objects.all()
    serializer_class = ToDoItemSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Return to-do items for the authenticated user."""
        return self.queryset.filter(todo_list__owner=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def task_recommendation(request):
    try:
        project_id = request.data.get('project_id')
        task_description = request.data.get('task_description')

        project = Project.objects.get(pk=project_id)

        if request.user != project.leader:
            return Response({"detail": "Only the project leader can access this endpoint."}, status=status.HTTP_403_FORBIDDEN)

        members = project.members.all()
        if not members:
            return Response({"detail": "No members found in the project."}, status=status.HTTP_400_BAD_REQUEST)

        resumes = "\n".join([f"Resume {i+1}: {member.resume_text}" for i, member in enumerate(members)])

        prompt = f"""
                    Please review the following resumes:
                    {resumes}
                    Considering the task description below:
                    {task_description}
                    Identify the resume number and the name of the candidate that best matches the task requirements. If no suitable match is found, state that no suitable resume is available.
                    Response format:
                    1. Resume number: [number], Name: [name]
                    2. Additional comments or reasoning
                    Please provide your response in plain text format without any Markdown formatting.
                    """

        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
        response = model.generate_content(prompt)

        # Access the text content from the response
        text_content = ""  # Initialize to empty string to handle potential errors gracefully
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
             text_content = response.candidates[0].content.parts[0].text

        return Response({"recommendation": text_content}, status=status.HTTP_200_OK)

    except Project.DoesNotExist:
        return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# def fetch_resumes(members):
#     resumes = []
#     for idx, member in enumerate(members, start=1):
#         resume_text = member.resume_text
#         if resume_text and resume_text.strip():  # Check if resume_text is not None and not empty after stripping whitespace
#             resumes.append(f"Resume {idx}:\n{resume_text}\n")

#     # Check if there are at least two valid resumes
#     if len(resumes) < 2:
#         return None
#     return resumes
