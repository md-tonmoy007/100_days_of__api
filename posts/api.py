from django.db.models import Q
from django.http import JsonResponse
from account.serializers import UserSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializers import PostSerializer
from .models import Post
from account.models import User


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def post_list(request):


    posts = Post.objects.all()


    serializer = PostSerializer(posts, many=True)

    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def post_list_profile(request, id):   
    user = User.objects.get(pk=id)
    posts = Post.objects.filter(created_by_id=id)
    
    posts_serializer = PostSerializer(posts, many=True)
    user_serializer = UserSerializer(user)
    
    return JsonResponse({
        'posts': posts_serializer.data,
        'user': user_serializer.data,
        # 'message': name,
    }, safe=False)
    