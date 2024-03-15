
from rest_framework import serializers

from account.serializers import UserSerializer

from .models import Post, PostAttachment

# class PostAttachmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PostAttachment
#         fields = ('id', 'get_image',)
        
        
class PostSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    # attachments = PostAttachmentSerializer(read_only=True, many=True)

    class Meta:
        model = Post
        fields = ('id', 'body', 'created_by', 'created_at_formatted')

