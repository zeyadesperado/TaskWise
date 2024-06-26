from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin
from django_extensions.db.models import TimeStampedModel
from django.db.models.signals import post_save
from django.dispatch import receiver
from .convert_resume import convert_file_to_text

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
    """User for the application."""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    resume_text = models.TextField(blank=True)
    resume_file = models.FileField(upload_to='resumes/',null=True,blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    #Setting the manager class to UserManager
    objects= UserManager()
    #Setting the email to be the unique identifier for authentication
    USERNAME_FIELD = 'email'
    #Setting the required field that the superuser has to enter
    REQUIRED_FIELDS = ('name',)
    def __str__(self):
        return self.name
    


class Project(TimeStampedModel):
    name = models.CharField(max_length=250)
    description = models.TextField()
    leader = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    members = models.ManyToManyField(User, related_name='projects', blank=True)

class Task(TimeStampedModel):
    name = models.CharField(max_length=250)
    description= models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    deadline= models.DateTimeField(blank=True,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment(TimeStampedModel):
    """comment for the project with userID and projectID and the comment it self with creationTime"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()

@receiver(post_save, sender=User)
def save_resume_text(sender, instance, **kwargs):
    if instance.resume_file:
        resume_file = str(instance.resume_file.path)  # Get the full path of the resume file
        resume_text = convert_file_to_text(resume_file)

        # Check if resume_text has changed
        if instance.resume_text != resume_text:
            print("Coneverting to resume_text...")
            instance.resume_text = resume_text
            instance.save()  # Save the instance to persist the changes
