from django.db.models import Q
from django.http import JsonResponse
from account.serializers import UserSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializers import PostSerializer, CommentSerializer
from .models import Post, Like, Comment, Project
from account.models import User
from .forms import PostForm, AttachmentForm, ProjectForm
from rest_framework import status



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
    


@api_view(['POST'])
def post_create(request):
    form = PostForm(request.POST)
    attachment = None
    attachment_form = AttachmentForm(request.POST, request.FILES)

    if attachment_form.is_valid():
        attachment = attachment_form.save(commit=False)
        attachment.created_by = request.user
        attachment.save()

    if form.is_valid():
        post = form.save(commit=False)
        post.created_by = request.user
        post.save()

        if attachment:
            post.attachments.add(attachment)

        user = request.user
        user.posts_count = user.posts_count + 1
        user.save()

        serializer = PostSerializer(post)

        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'error': 'add somehting here later!...'})
    
    
    

@api_view(['DELETE'])
def post_delete(request, pk):
    post = Post.objects.filter(created_by=request.user).get(pk=pk)
    post.delete()

    return JsonResponse({'message': 'post deleted'})





@api_view(['POST'])
def post_like(request, pk):
    post = Post.objects.get(pk=pk)
    print("Hello")
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




    