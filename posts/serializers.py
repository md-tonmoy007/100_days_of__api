
from rest_framework import serializers

from account.serializers import UserSerializer

from .models import *

# class PostAttachmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PostAttachment
#         fields = ('id', 'get_image',)


class LikeSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'created_by',)


class CommentSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'body', 'created_by', 'created_at_formatted',)


class ThreadSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    participants_count = serializers.ReadOnlyField()
    posts_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Thread
        fields = ('id', 'topic', 'display_name', 'description', 'created_by', 
                 'created_at', 'participants_count', 'posts_count')


class UserThreadSerializer(serializers.ModelSerializer):
    thread = ThreadSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = UserThread
        fields = ('id', 'thread', 'user', 'current_day', 'posts_count', 'is_completed', 
                 'started_at', 'completed_at', 'progress_percentage', 'is_active')


class PostSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    likes = LikeSerializer(read_only=True, many=True)
    likes_count = serializers.ReadOnlyField()
    comments = CommentSerializer(read_only=True, many=True)
    comments_count = serializers.ReadOnlyField()
    
    # Thread information
    user_thread = UserThreadSerializer(read_only=True)
    thread_info = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = ('id', 'body', 'likes_count', 'created_by', 'created_at_formatted', 
                 'comments', 'comments_count', 'likes', 'user_thread', 'day_number', 'thread_info')


class PostCreateSerializer(serializers.ModelSerializer):
    user_thread_id = serializers.UUIDField(required=False, allow_null=True)
    day_number = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Post
        fields = ('body', 'user_thread_id', 'day_number')
    
    def validate(self, attrs):
        # If thread is specified, day_number should also be specified
        user_thread_id = attrs.get('user_thread_id')
        day_number = attrs.get('day_number')
        
        if user_thread_id and not day_number:
            raise serializers.ValidationError("Day number is required when posting to a thread")
        
        if day_number and not user_thread_id:
            raise serializers.ValidationError("Thread is required when specifying a day number")
            
        return attrs


class ThreadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ('topic', 'description')
    
    def validate_topic(self, value):
        # Normalize topic
        return value.lower().strip()


class JoinThreadSerializer(serializers.Serializer):
    thread_id = serializers.UUIDField()


class ProjectSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Project
        fields = ('id', 'name', 'created_at', 'description',)
