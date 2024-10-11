from rest_framework import serializers
from posts.models import Post



class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'body','likes_count', 'created_by', 'created_at_formatted', 'comments', 'comments_count')

