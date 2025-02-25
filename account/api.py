from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes  # type: ignore
from .models import *
from posts.models import Post
from posts.serializers import PostSerializer
from rest_framework.views import APIView # type: ignore
from rest_framework import generics # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from .forms import SignupForm, LoginSerializer, ProfileForm
import json
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
import jwt
from django.conf import settings
from .serializers import EmailVerificationSerializer,ResetPasswordEmailRequestSerializer,SetNewPasswordSerializer,UserSerializer, FriendshipRequestSerializer
from drf_yasg.utils import swagger_auto_schema # type: ignore
from drf_yasg import openapi # type: ignore
import json
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.exceptions import ObjectDoesNotExist


@api_view(['GET'])
def me(request):
    user_serializer = UserSerializer(request.user)
    return JsonResponse({
        'user': user_serializer.data,
    })
    
@api_view(['GET'])
def post_list_profile(request, id):   
    user = User.objects.get(pk=id)
    posts = Post.objects.filter(created_by_id=id)
    is_my_profile = str(request.user.id) == id
    status = "not_friends"


    # check1 = FriendshipRequest.objects.filter(created_for=request.user).filter(created_by=user)
    try:
        frnd_requests1 = FriendshipRequest.objects.filter(created_for=request.user).get(created_by=user)
        if frnd_requests1.status == 'accepted':
            status = "Friends"
        elif frnd_requests1.status == 'sent':
            status = "Accept request"
    except FriendshipRequest.DoesNotExist:
        try:
            frnd_requests2 = FriendshipRequest.objects.filter(created_for=user).get(created_by=request.user)
            if frnd_requests2.status == 'accepted':
                status = "Friends"
            elif frnd_requests2.status == 'sent':
                status = "Request sent"
                
        except FriendshipRequest.DoesNotExist:
            frnd_requests = None  # or handle it in another way
            status = "add friend"

    
    
    
    
    
    

    
    posts_serializer = PostSerializer(posts, many=True)
    user_serializer = UserSerializer(user)
    # request_status = FriendshipRequestSerializer(check, many=True)
    # print(frnd_requests1.data[0]['status'])
    
    # if not is_my_profile:
    #     if  frnd_requests != None:
    #         status = "add friend"
            
    #         try:
    #             # status = str(request_status.data[0]['status'])
                
    #             print(frnd_requests2.status)
    #             if (frnd_requests1 and frnd_requests1.status == 'accepted') or (frnd_requests2 and frnd_requests2.status == 'accepted'):
    #                 status = "Friends"
    #                 print("aldkfjasdlkfj")
    #             elif frnd_requests1.status == 'sent':
    #                 status = "Accept request"
    #                 print("alksdfjasdlkfjasdfjalskdjflaksdjf")
    #             elif frnd_requests2.status == 'sent':
    #                 status = "Request sent"
    #                 print("alksdfjalksdjflkasjdflkajsdlfkjasdlkkfjskldkjflkaskdjf")

                
    #         except :
    #             status =   "something went wrong"
    
    
    return JsonResponse({
        'posts': posts_serializer.data,
        'user': user_serializer.data,   
        'my_profile': is_my_profile,
        'status': status,
        # 'message': name,
    }, safe=False)
    


    
@api_view(['GET'])
def authenticated(request):
    return JsonResponse({
        'authenticated': request.user.is_authenticated,
    })

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def signup(request):
    data = request.data
    message = 'success'
    
    
    form = SignupForm({
        'email': data.get('email'),
        'name': data.get('name'),
        'password1': data.get('password1'),
        'password2': data.get('password2'),
    })
    
    
    if form.is_valid():
        user = form.save()
        

    else:
        print(form.errors.as_json())
        message = "error"
    
        form_errors = form.errors.as_json()

        json_response = json.loads(form_errors)
        messages_only = {}
        first_error_message = next((error["message"] for errors in json_response.values() for error in errors), None)
        
        return JsonResponse(
        {
            'status': message,
                'messages': first_error_message,
            
            }
        )
        
        
    acc = User.objects.get(email=user.email)
    token = RefreshToken.for_user(acc).access_token
    current_site = get_current_site(request).domain
    relativeLink = reverse('email-verify')
    #+current_site+relativeLink+
    absurl = "http://localhost:3000/email-verify/?token="+str(token)  
    email_body = 'Hi '+user.name + \
        ' Use the link below to verify your email \n' + absurl
    data = {'email_body': email_body, 'to_email': user.email,
            'email_subject': 'Verify your email'}
    
    
    Util.send_email(data)
    
    return JsonResponse({
            'status': message,
            'email': user.email,
            'name': user.name,
        })
    
    
@authentication_classes([])
@permission_classes([])
class VerifyEmail(APIView):
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
        
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return JsonResponse({
            'email': user.email,
            'name': user.name,
        })
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError as e:
            return Response({'error': 'Invalid token', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class LogoutView(APIView):
    permission_classes = []
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        

@authentication_classes([])
@permission_classes([])      
class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@authentication_classes([])
@permission_classes([])
class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            # redirect_url = request.data.get('redirect_url', '')
            absurl =  "http://localhost:3000" + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                absurl               
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            Util.send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
    
    
    
@authentication_classes([])
@permission_classes([])  
class PasswordTokenCheckAPI(generics.GenericAPIView):
    # serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'checkError: Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)
                # if len(redirect_url) > 3:
                #     return CustomRedirect(redirect_url+'?token_valid=False')
                # else:
                #     return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

            # if redirect_url and len(redirect_url) > 3:
            #     return CustomRedirect(redirect_url+'?token_valid=True&message=Credentials Valid&uidb64='+uidb64+'&token='+token)
            # else:
            #     return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')
            return Response({'success': True, 'message':'valid','uidb64':uidb64, 'token':token })

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)

                    # return CustomRedirect(redirect_url+'?token_valid=False')
                    
            except UnboundLocalError as e:
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([])
@permission_classes([])  
class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)
    
    
    
    
@api_view(['POST'])
def editprofile(request):
    user = request.user
    email = request.data.get('email')
    name = request.data.get('name')
    
    print(type(user), email, name)

    if User.objects.exclude(id=user.id).filter(email=email).exists():
        return JsonResponse({'message': 'email already exists'})
    else:
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save() 
            serializer = UserSerializer(user)
            return JsonResponse({'message': 'information updated', 'user': serializer.data})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
        
        
@api_view(['GET'])
def friends(request, pk):
    user = User.objects.get(pk=pk)
    frnd_requests = []
    sent_requests = []
    
    requests_data = list()
    sent_requests_data = list()
    sent_request_confirm = [] 

    if user == request.user:
        frnd_requests = FriendshipRequest.objects.filter(created_for=request.user, status=FriendshipRequest.SENT)
        frnd_requests = FriendshipRequestSerializer(frnd_requests, many=True)
        
        for req in frnd_requests.data:
            requests_data.append(req['created_by'])
        
        sent_requests = FriendshipRequest.objects.filter(created_by=request.user, status=FriendshipRequest.SENT)
        sent_requests = FriendshipRequestSerializer(sent_requests, many=True)
        
        for req in sent_requests.data:
            sent_requests_data.append(req['created_for'])

            
        for uid in sent_requests_data:
            s_user = User.objects.get(pk=uid)
            user_serializer = UserSerializer(s_user)
            print(s_user)
            sent_request_confirm.append(user_serializer.data)
            
        

    friends = user.friends.all()
    
    print(requests_data)
    print("------------------------------------------")
    print(sent_requests_data)

    return JsonResponse({
        'user': UserSerializer(user).data,
        'friends': UserSerializer(friends, many=True).data,
        'requests': requests_data,
        'sent_requests': sent_request_confirm,
    }, safe=False)
        

        
@api_view(['POST'])
def send_friendship_request(request, pk):
    user = User.objects.get(pk=pk)
    
    print(request.user)

    check1 = FriendshipRequest.objects.filter(created_for=request.user).filter(created_by=user)
    check2 = FriendshipRequest.objects.filter(created_for=user).filter(created_by=request.user)

    if not check1 or not check2:
        friendrequest = FriendshipRequest.objects.create(created_for=user, created_by=request.user)
       

        return JsonResponse({'message': 'friendship request created'})
    else:
        return JsonResponse({'message': 'request already sent'})
    
    
@api_view(['POST'])
def handle_request(request, pk, status):
    # # user = User.objects.get(pk=pk)
    # # print(user.email)
    # print(request.user)
    friendship_request = FriendshipRequest.objects.get(pk=pk)
    user1 = friendship_request.created_for
    user2 = friendship_request.created_by
    print(friendship_request)
    print("\nemails:", request.user.email, user1.email, user2.email)
    if request.user.email == user1.email:
        print("hello world")
        friendship_request.status = status
        friendship_request.save()

    if friendship_request.status == 'accepted':
        user1.friends.add(user2)
        user1.friends_count = user1.friends_count + 1
        user1.save()

        # request_user = request.user
        user2.friends_count = user2.friends_count + 1
        user2.save()
        JsonResponse({'message': 'not friends'})
        


    return JsonResponse({'message': 'friendship request updated'})


@api_view(['POST'])
def handle_request_profile(request, pk, status):
    print(request.user)
    print(pk)
    friendship_request = FriendshipRequest.objects.filter(created_for=request.user).get(created_by=pk)
    user1 = friendship_request.created_for
    user2 = friendship_request.created_by
    print(friendship_request)
    print("\nemails:", request.user.email, user1.email, user2.email)
    if request.user.email == user1.email:
        print("hello world")
        friendship_request.status = status
        friendship_request.save()

    if friendship_request.status == 'accepted':
        user1.friends.add(user2)
        user1.friends_count = user1.friends_count + 1
        user1.save()

        # request_user = request.user
        user2.friends_count = user2.friends_count + 1
        user2.save()
        JsonResponse({'message': 'not friends'})
        


    return JsonResponse({'message': 'friendship request updated'})