from django.db.models import Q
# from rest_framework.generics import ListAPIView
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from account.serializers import UserSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializers import PostSerializer, CommentSerializer, ProjectSerializer
from .models import Post, Like, Comment, Project
from account.models import User
from .forms import PostForm, AttachmentForm, ProjectForm
from rest_framework import status, viewsets  
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def post_list(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return JsonResponse(serializer.data, safe=False)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]

@api_view(['GET'])
def post_detail(request, pk):
    liked = ""
    try:
        post = Post.objects.get(pk=pk)
        user = post.created_by
        
        if post.likes.filter(created_by=request.user).exists():
            liked = 1
        else:
            liked = 0

        post_serializer = PostSerializer(post)
        # user_serializer = UserSerializer(user)

        return JsonResponse({
            'post': post_serializer.data,
            'liked': liked,
            # 'user': user_serializer.data
        }, safe=False)

    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








@api_view(['POST'])
def post_create(request):
    # form = PostForm(request.POST)
    body = request.data.get('body')  # Retrieve body from JSON data
    tag = request.data.get('tag')    # Retrieve tag from JSON data
    
    
    try:
        list_tag = Project(name=tag)
        
    except:
        pass
    
    print(f"Body: {body}, Tag: {tag}")  # Check the received values
    return Response({'message': 'Post created successfully!'})
    # attachment = None
    # attachment_form = AttachmentForm(request.POST, request.FILES)

    # if attachment_form.is_valid():
    #     attachment = attachment_form.save(commit=False)
    #     attachment.created_by = request.user
    #     attachment.save()

    # if form.is_valid():
    #     post = form.save(commit=False)
    #     post.created_by = request.user
    #     post.save()

    #     # if attachment:
    #     #     post.attachments.add(attachment)

    #     user = request.user
    #     user.posts_count = user.posts_count + 1
    #     user.save()

    #     serializer = PostSerializer(post)

    #     return JsonResponse(serializer.data, safe=False)
    # else:
    #     return JsonResponse({'error': 'add somehting here later!...'})
    
    
    

@api_view(['DELETE'])
def post_delete(request, pk):
    post = Post.objects.filter(created_by=request.user).get(pk=pk)
    post.delete()

    return JsonResponse({'message': 'post deleted'})





@api_view(['POST'])
def post_like(request, pk):
    post = Post.objects.get(pk=pk)
    print("Hello")
    if post.likes.filter(created_by=request.user).exists():
        like = Like.objects.get(created_by=request.user)
        post.likes_count = post.likes_count - 1
        post.likes.remove(like)
        post.save()
        like.delete()
        return JsonResponse({'message': 'like deleted'})    
        
        
        
    if not post.likes.filter(created_by=request.user):
        like = Like.objects.create(created_by=request.user)

        post = Post.objects.get(pk=pk)
        post.likes_count = post.likes_count + 1
        post.likes.add(like)
        post.save()


        return JsonResponse({'message': 0})
    else:
        return JsonResponse({'message': 1})




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



@api_view(['POST'])
def project_create(request):
    form = ProjectForm(request.POST)
    if form.is_valid():
        form.save()
    return JsonResponse({'message': 'hola'})


@api_view(['GET'])
def trending(request):
    projects = Project.objects.all()
    projects = projects[0:5]
    serializer = ProjectSerializer(projects, many=True)
    return JsonResponse(serializer.data, safe=False)

    