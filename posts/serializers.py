
from rest_framework import serializers

from account.serializers import UserSerializer

from .models import *

# class PostAttachmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PostAttachment
#         fields = ('id', 'get_image',)
        
        
class PostSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    # attachments = PostAttachmentSerializer(read_only=True, many=True)

    class Meta:
        model = Post
        fields = ('id', 'body','likes_count', 'created_by', 'created_at_formatted', 'comments', 'comments_count')

class CommentSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'body', 'created_by', 'created_at_formatted',)


class ProjectSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Project
        fields = ('id', 'name', 'created_at', 'description',)
