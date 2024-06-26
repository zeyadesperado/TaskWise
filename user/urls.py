from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path,include

router = DefaultRouter()
router.register('project', views.ProjectViewSet)
router.register('task', views.TaskViewSet)
router.register('comment', views.CommentViewset)
urlpatterns = [
    path('login/',views.UserLoginApiView.as_view()),
    path('create/', views.CreateUserView.as_view()),
    path('manage/', views.ManageUserView.as_view()),
    
    path('',include(router.urls)),
]

