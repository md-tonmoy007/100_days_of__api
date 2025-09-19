from django.db.models import Q
from django.http import JsonResponse

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from account.models import User
from account.serializers import UserSerializer
from posts.models import Post
from posts.serializers import PostSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search(request):
    try:
        data = request.data
        query = data.get('query', '').strip()
        
        print(f"Search request from user {request.user.name} (ID: {request.user.id})")
        print(f"Search query: '{query}'")
        
        if not query:
            return JsonResponse({
                'users': [],
                'posts': []
            }, safe=False)

        # Search for users by name or email
        users = User.objects.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        ).exclude(id=request.user.id)  # Exclude current user
        
        print(f"Found {users.count()} users matching query")
        for user in users:
            print(f"  - User: {user.name} ({user.email})")
        
        users_serializer = UserSerializer(users, many=True)

        # Search for posts by body content
        posts = Post.objects.filter(body__icontains=query).order_by('-created_at')
        
        print(f"Found {posts.count()} posts matching query")
        for post in posts[:3]:  # Show first 3 posts
            print(f"  - Post: {post.body[:50]}... by {post.created_by.name}")
        
        posts_serializer = PostSerializer(posts, many=True)

        result = {
            'users': users_serializer.data,
            'posts': posts_serializer.data
        }
        
        print(f"Returning {len(result['users'])} users and {len(result['posts'])} posts")
        
        return JsonResponse(result, safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Search failed',
            'details': str(e)
        }, status=500)