from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path,include

router = DefaultRouter()
router.register('users',views.UserViewSet)

urlpatterns = [
    path('',include(router.urls)),
]

