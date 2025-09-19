from django.http import JsonResponse
from django.db.models import Q, Count, Max
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.paginator import Paginator
from .serializers import (
    PostSerializer, CommentSerializer, ProjectSerializer,
    ThreadSerializer, UserThreadSerializer, ThreadCreateSerializer,
    JoinThreadSerializer, PostCreateSerializer
)
from .models import Post, Like, Comment, Project, Thread, UserThread

# List all posts with pagination and personalized feed filtering
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def post_list(request):
    try:
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))  # Default 10 posts per page
        
        # Ensure reasonable limits
        limit = min(limit, 50)  # Max 50 posts per request
        
        # Get the current user
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        current_user = request.user
        
        # Build personalized feed query based on conditions:
        # 1. User's own posts
        # 2. Posts from threads the user has joined
        # 3. Posts from friends
        
        # Condition 1: User's own posts
        own_posts_query = Q(created_by=current_user)
        
        # Condition 2: Posts from threads the user has joined
        # Get all threads the user has joined
        user_threads = UserThread.objects.filter(
            user=current_user, 
            is_active=True
        ).values_list('thread_id', flat=True)
        
        # Get posts from these threads (from any user in those threads)
        thread_posts_query = Q(user_thread__thread_id__in=user_threads)
        
        # Condition 3: Posts from friends
        # Get all friends of the current user
        friends = current_user.friends.all().values_list('id', flat=True)
        friends_posts_query = Q(created_by__id__in=friends)
        
        # Combine all conditions with OR
        feed_query = own_posts_query | thread_posts_query | friends_posts_query
        
        # Get filtered posts ordered by creation date (newest first)
        # Use select_related and prefetch_related for optimization
        posts_queryset = Post.objects.filter(feed_query).select_related(
            'created_by', 'user_thread__thread'
        ).prefetch_related(
            'likes', 'comments'
        ).order_by('-created_at').distinct()
        
        # Debug information
        total_posts_before_filter = Post.objects.count()
        filtered_posts_count = posts_queryset.count()
        
        print(f"DEBUG: User {current_user.name} (ID: {current_user.id})")
        print(f"DEBUG: Total posts in DB: {total_posts_before_filter}")
        print(f"DEBUG: User threads: {list(user_threads)}")
        print(f"DEBUG: Friends: {list(friends)}")
        print(f"DEBUG: Filtered posts count: {filtered_posts_count}")
        
        # Apply pagination
        paginator = Paginator(posts_queryset, limit)
        posts_page = paginator.get_page(page)
        
        # Serialize the posts
        serializer = PostSerializer(posts_page.object_list, many=True)
        
        # Return paginated response
        return JsonResponse({
            'posts': serializer.data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_posts': paginator.count,
                'has_next': posts_page.has_next(),
                'has_previous': posts_page.has_previous(),
                'next_page': page + 1 if posts_page.has_next() else None,
                'previous_page': page - 1 if posts_page.has_previous() else None,
            },
            'feed_info': {
                'user_threads_count': len(user_threads),
                'friends_count': len(friends),
                'filtering_applied': True,
                'user_id': str(current_user.id),
                'total_posts_in_db': total_posts_before_filter,
                'filtered_posts_count': filtered_posts_count
            }
        }, safe=False)
        
    except ValueError:
        return JsonResponse({'error': 'Invalid page or limit parameter'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Public feed - shows all posts (for admin/public viewing)
@api_view(['GET'])
@permission_classes([AllowAny])
def public_post_list(request):
    try:
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))  # Default 10 posts per page
        
        # Ensure reasonable limits
        limit = min(limit, 50)  # Max 50 posts per request
        
        # Get all posts ordered by creation date (newest first)
        posts_queryset = Post.objects.all().order_by('-created_at')
        
        # Apply pagination
        paginator = Paginator(posts_queryset, limit)
        posts_page = paginator.get_page(page)
        
        # Serialize the posts
        serializer = PostSerializer(posts_page.object_list, many=True)
        
        # Return paginated response
        return JsonResponse({
            'posts': serializer.data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_posts': paginator.count,
                'has_next': posts_page.has_next(),
                'has_previous': posts_page.has_previous(),
                'next_page': page + 1 if posts_page.has_next() else None,
                'previous_page': page - 1 if posts_page.has_previous() else None,
            },
            'feed_info': {
                'filtering_applied': False,
                'public_feed': True
            }
        }, safe=False)
        
    except ValueError:
        return JsonResponse({'error': 'Invalid page or limit parameter'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
@permission_classes([IsAuthenticated])
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
        
        # Check if filtering by a specific user
        user_id = request.GET.get('user_id')
        
        if user_id:
            # Filter posts by specific user
            posts = Post.objects.filter(
                user_thread__thread=thread,
                created_by__id=user_id
            ).order_by('day_number', 'created_at')  # Sort by day number first, then by creation time
            
            # Get the specific user's thread participation
            user_thread = UserThread.objects.filter(thread=thread, user__id=user_id).first()
        else:
            # Get all thread posts sorted by day number (ascending)
            posts = Post.objects.filter(
                user_thread__thread=thread
            ).order_by('day_number', 'created_at')  # Sort by day number first, then by creation time
            
            # Check if current user is in this thread
            user_thread = None
            if request.user.is_authenticated:
                user_thread = UserThread.objects.filter(thread=thread, user=request.user).first()
        
        thread_serializer = ThreadSerializer(thread)
        posts_serializer = PostSerializer(posts, many=True)
        user_thread_serializer = UserThreadSerializer(user_thread) if user_thread else None
        
        return JsonResponse({
            'thread': thread_serializer.data,
            'posts': posts_serializer.data,
            'user_thread': user_thread_serializer.data if user_thread_serializer else None,
            'filtered_by_user': user_id is not None
        }, safe=False)
    except Thread.DoesNotExist:
        return JsonResponse({'error': 'Thread not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========== SIDEBAR API ENDPOINTS ==========

# Get recently active threads
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_threads(request):
    try:
        # Get threads with recent posts from user's friends or public threads
        recent_threads = Thread.objects.filter(
            is_active=True,
            participants__posts__created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).annotate(
            active_participants_count=Count('participants', distinct=True),
            total_posts_count=Count('participants__posts', distinct=True),
            latest_post=Max('participants__posts__created_at')
        ).order_by('-latest_post')[:10]
        
        # Add name field to match frontend expectations
        threads_data = []
        for thread in recent_threads:
            thread_data = {
                'id': thread.id,
                'name': thread.topic,  # Using topic as name
                'description': thread.description,
                'participants_count': thread.active_participants_count,
                'posts_count': thread.total_posts_count,
                'latest_post': thread.latest_post
            }
            threads_data.append(thread_data)
        
        return JsonResponse(threads_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Get suggested threads
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def suggested_threads(request):
    try:
        # Get threads the user hasn't joined yet
        user_thread_ids = UserThread.objects.filter(user=request.user).values_list('thread_id', flat=True)
        
        suggested_threads = Thread.objects.filter(
            is_active=True
        ).exclude(
            id__in=user_thread_ids
        ).annotate(
            active_participants_count=Count('participants', distinct=True),
            total_posts_count=Count('participants__posts', distinct=True)
        ).order_by('-active_participants_count')[:10]
        
        # Add name field to match frontend expectations
        threads_data = []
        for thread in suggested_threads:
            thread_data = {
                'id': thread.id,
                'name': thread.topic,  # Using topic as name
                'description': thread.description,
                'participants_count': thread.active_participants_count,
                'posts_count': thread.total_posts_count
            }
            threads_data.append(thread_data)
        
        return JsonResponse(threads_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)