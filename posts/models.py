from django.db import models
import uuid

from django.conf import settings
from django.db import models
from django.utils.timesince import timesince

from account.models import User
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class PostAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='post_attachments')
    created_by = models.ForeignKey(User, related_name='post_attachments', on_delete=models.CASCADE)
    
    
class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


   
   

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    body = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
    
    def created_at_formatted(self):
       return timesince(self.created_at)


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    name = models.TextField(blank=True, null=False, unique=True)

    number = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name # TODO
    
    class Meta:
        ordering = ('-number',)
    




class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    body = models.TextField(blank=True, null=True)

    # attachments = models.ManyToManyField(PostAttachment, blank=True)
    likes = models.ManyToManyField(Like, blank=True)
    likes_count = models.IntegerField(default=0)

    comments = models.ManyToManyField(Comment, blank=True)
    comments_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE, db_constraint=False)
    project = models.ForeignKey(Project, related_name='projects', on_delete=models.CASCADE, default='f1ea2dfe-ae3f-4088-964f-5400121967b4')
    


    class Meta:
        ordering = ('-created_at',)
    
    def created_at_formatted(self):
       return timesince(self.created_at)
   
   
@receiver(post_save, sender=Post)
def increment_project_post_count(sender, instance, created, **kwargs):
    if created:
        project = instance.project
        project.number += 1
        project.save()

'''
    Every time a user creates a post. We will add +1 to the project which was selected.
    then we will sort it according to number of the project
    top 5 projects will on trends.
'''
   
