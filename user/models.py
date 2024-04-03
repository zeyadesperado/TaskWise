from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self,email,name,password):
        if not email:
            raise ValueError('Email is required!!')
        email= self.normalize_email(email)
        user= self.model(email=email,name=name)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self,email,name,password):
        user= self.create_user(email,name,password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser,PermissionsMixin):
    #Fields 
    email = models.EmailField(unique=True) 
    name = models.CharField(max_length=100) 
    password = models.CharField(max_length=100)
    profile_info = models.TextField(blank=True)
    resume = models.TextField(blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default = True)
    is_staff = models.BooleanField(default = False)
    #Setting the manager class to UserManager
    objects= UserManager()
    #Setting the email to be the unique identifier for authentication
    USERNAME_FIELD = 'email'
    #Setting the required field that the superuser has to enter 
    REQUIRED_FIELDS = ('name',)
    def __str__(self):
        return self.email


class Project(models.Model):
    name= models.CharField(max_length=100)
    description= models.TextField()
    leader_id= models.ForeignKey(User,on_delete=models.CASCADE)
    creation_time= models.DateTimeField(auto_now_add=True)
    dead_line= models.DateTimeField(blank=True)
