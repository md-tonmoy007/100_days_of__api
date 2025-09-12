from django.db import models
import uuid

from django.conf import settings
from django.db import models
from django.utils.timesince import timesince
from django.utils import timezone

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


class Thread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.CharField(max_length=100, help_text="e.g., 'Python', 'React', 'Machine Learning'")
    created_by = models.ForeignKey(User, related_name='created_threads', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Thread statistics
    posts_count = models.IntegerField(default=0)
    participants_count = models.IntegerField(default=0)
    
    # Thread settings
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True, help_text="Optional description of the thread")
    
    class Meta:
        ordering = ('-updated_at',)
        indexes = [
            models.Index(fields=['topic', 'created_by']),
            models.Index(fields=['-updated_at']),
        ]
    
    def __str__(self):
        return f"100 Days of {self.topic} by {self.created_by.name}"
    
    @property
    def display_name(self):
        return f"100 Days of {self.topic}"


class UserThread(models.Model):
    """Individual user's participation in a thread"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='user_threads', on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, related_name='participants', on_delete=models.CASCADE)
    
    # Progress tracking
    current_day = models.IntegerField(default=0)
    posts_count = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    last_post_at = models.DateTimeField(null=True, blank=True)
    
    # Status tracking
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'thread')
        ordering = ('-last_post_at',)
        indexes = [
            models.Index(fields=['user', 'thread']),
            models.Index(fields=['-last_post_at']),
        ]
    
    def __str__(self):
        return f"{self.user.name} - {self.thread.display_name} (Day {self.current_day})"
    
    @property
    def progress_percentage(self):
        return min((self.current_day / 100) * 100, 100)
    
    def mark_completed(self):
        if self.current_day >= 100 and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save()
    





class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    body = models.TextField(blank=True, null=True)
    
    # Thread relationship
    user_thread = models.ForeignKey(UserThread, related_name='posts', on_delete=models.CASCADE, null=True, blank=True)
    day_number = models.IntegerField(null=True, blank=True, help_text="Day number in the 100-day challenge")
    
    # Legacy fields (keep for backward compatibility)
    # attachments = models.ManyToManyField(PostAttachment, blank=True)
    likes = models.ManyToManyField(Like, blank=True)
    likes_count = models.IntegerField(default=0)
    comments = models.ManyToManyField(Comment, blank=True)
    comments_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE, db_constraint=False)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['user_thread', 'day_number']),
            models.Index(fields=['-created_at']),
        ]
    
    def created_at_formatted(self):
        return timesince(self.created_at)
    
    @property
    def thread_info(self):
        """Get thread information for this post"""
        if self.user_thread:
            return {
                'thread_id': self.user_thread.thread.id,
                'thread_topic': self.user_thread.thread.topic,
                'thread_display_name': self.user_thread.thread.display_name,
                'day_number': self.day_number,
                'user_progress': self.user_thread.current_day
            }
        return None

'''
    Every time a user creates a post. We will add +1 to the project which was selected.
    then we will sort it according to number of the project
    top 5 projects will on trends.
'''
   
