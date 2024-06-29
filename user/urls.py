from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path,include

router = DefaultRouter()
router.register('project', views.ProjectViewSet)
router.register('task', views.TaskViewSet)
router.register('comment', views.CommentViewset)
router.register('todolist', views.ToDoListViewSet)
router.register('todoitem', views.ToDoItemViewSet)
urlpatterns = [
    path('login/',views.UserLoginApiView.as_view()),
    path('create/', views.CreateUserView.as_view()),
    path('manage/', views.ManageUserView.as_view()),
    path('recommend/', views.TaskRecommendation, name='TaskRecommendation'),
    path('',include(router.urls)),
]

