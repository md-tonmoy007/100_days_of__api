from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from .serializers import (
    PostSerializer, CommentSerializer, ProjectSerializer,
    ThreadSerializer, UserThreadSerializer, ThreadCreateSerializer,
    JoinThreadSerializer, PostCreateSerializer
)
from .models import Post, Like, Comment, Project, Thread, UserThread

# List all posts
@api_view(['GET'])
def post_list(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return JsonResponse(serializer.data, safe=False)

# Post detail with like status
@api_view(['GET'])
def post_detail(request, pk):
    try:
        post = Post.objects.get(pk=pk)
        liked = post.likes.filter(created_by=request.user).exists()
        post_serializer = PostSerializer(post)
        return JsonResponse({
            'post': post_serializer.data,
            'liked': int(liked)
        }, safe=False)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Create a post (body only or with thread)
@api_view(['POST'])
def post_create(request):
    serializer = PostCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        data = serializer.validated_data
        user_thread_id = data.get('user_thread_id')
        day_number = data.get('day_number')
        
        # Validate user thread ownership if specified
        user_thread = None
        if user_thread_id:
            try:
                user_thread = UserThread.objects.get(id=user_thread_id, user=request.user)
                # Validate day number
                if day_number > user_thread.current_day + 1:
                    return JsonResponse({
                        'error': f'You can only post for day {user_thread.current_day + 1} or earlier'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except UserThread.DoesNotExist:
                return JsonResponse({'error': 'Thread not found or not accessible'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create the post
        post = Post.objects.create(
            body=data['body'],
            created_by=request.user,
            user_thread=user_thread,
            day_number=day_number
        )
        
        # Update user thread progress if this is a new day
        if user_thread and day_number and day_number > user_thread.current_day:
            user_thread.current_day = day_number
            if day_number >= 100:
                user_thread.is_completed = True
                user_thread.completed_at = timezone.now()
            user_thread.save()
        
        serializer = PostSerializer(post)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_201_CREATED)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Delete a post
@api_view(['DELETE'])
def post_delete(request, pk):
    try:
        post = Post.objects.filter(created_by=request.user).get(pk=pk)
        post.delete()
        return JsonResponse({'message': 'post deleted'})
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Like/unlike a post
@api_view(['POST'])
def post_like(request, pk):
    try:
        post = Post.objects.get(pk=pk)
        like = post.likes.filter(created_by=request.user).first()
        if like:
            post.likes_count = post.likes_count - 1
            post.likes.remove(like)
            post.save()
            like.delete()
            return JsonResponse({'message': 'like deleted'})
        else:
            like = Like.objects.create(created_by=request.user)
            post.likes_count = post.likes_count + 1
            post.likes.add(like)
            post.save()
            return JsonResponse({'message': 0})
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Add a comment to a post
@api_view(['POST'])
def post_create_comment(request, pk):
    try:
        comment = Comment.objects.create(body=request.data.get('body'), created_by=request.user)
        post = Post.objects.get(pk=pk)
        post.comments.add(comment)
        post.comments_count = post.comments_count + 1
        post.save()
        serializer = CommentSerializer(comment)
        return JsonResponse(serializer.data, safe=False)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Show a single comment
@api_view(['GET'])
def comment_show(request, pk):
    try:
        comment = Comment.objects.get(pk=pk)
        serializer = CommentSerializer(comment)
        return JsonResponse(serializer.data, safe=False)
    except Comment.DoesNotExist:
        return JsonResponse({'error': 'comment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========== THREAD API ENDPOINTS ==========

# List all threads
@api_view(['GET'])
def thread_list(request):
    threads = Thread.objects.filter(is_active=True).order_by('-created_at')
    serializer = ThreadSerializer(threads, many=True)
    return JsonResponse(serializer.data, safe=False)

# Create a new thread
@api_view(['POST'])
def thread_create(request):
    serializer = ThreadCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        data = serializer.validated_data
        topic = data['topic']
        
        # Check if thread with this topic already exists
        existing_thread = Thread.objects.filter(topic=topic).first()
        if existing_thread:
            return JsonResponse({'error': 'A thread with this topic already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create thread
        thread = Thread.objects.create(
            topic=topic,
            description=data.get('description', ''),
            created_by=request.user
        )
        
        # Auto-join creator to thread
        UserThread.objects.create(
            thread=thread,
            user=request.user,
            current_day=0
        )
        
        serializer = ThreadSerializer(thread)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_201_CREATED)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Join a thread
@api_view(['POST'])
def thread_join(request):
    serializer = JoinThreadSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        thread_id = serializer.validated_data['thread_id']
        thread = Thread.objects.get(id=thread_id, is_active=True)
        
        # Check if user already joined
        user_thread = UserThread.objects.filter(thread=thread, user=request.user).first()
        if user_thread:
            return JsonResponse({'error': 'You have already joined this thread'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Join thread
        user_thread = UserThread.objects.create(
            thread=thread,
            user=request.user,
            current_day=0
        )
        
        serializer = UserThreadSerializer(user_thread)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_201_CREATED)
    except Thread.DoesNotExist:
        return JsonResponse({'error': 'Thread not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Get user's threads
@api_view(['GET'])
def user_threads(request):
    user_threads = UserThread.objects.filter(user=request.user).order_by('-started_at')
    serializer = UserThreadSerializer(user_threads, many=True)
    return JsonResponse(serializer.data, safe=False)

# Get thread details with posts
@api_view(['GET'])
def thread_detail(request, pk):
    try:
        thread = Thread.objects.get(pk=pk, is_active=True)
        
        # Get thread posts
        posts = Post.objects.filter(
            user_thread__thread=thread
        ).order_by('-created_at')[:20]  # Limit to recent posts
        
        # Check if user is in this thread
        user_thread = None
        if request.user.is_authenticated:
            user_thread = UserThread.objects.filter(thread=thread, user=request.user).first()
        
        thread_serializer = ThreadSerializer(thread)
        posts_serializer = PostSerializer(posts, many=True)
        user_thread_serializer = UserThreadSerializer(user_thread) if user_thread else None
        
        return JsonResponse({
            'thread': thread_serializer.data,
            'posts': posts_serializer.data,
            'user_thread': user_thread_serializer.data if user_thread_serializer else None
        }, safe=False)
    except Thread.DoesNotExist:
        return JsonResponse({'error': 'Thread not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)