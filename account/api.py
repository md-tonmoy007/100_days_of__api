from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .models import User
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .forms import SignupForm
import json
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
import jwt
from django.conf import settings
from .serializers import EmailVerificationSerializer,ResetPasswordEmailRequestSerializer,SetNewPasswordSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

@api_view(['GET'])
def me(request):
    return JsonResponse({
        'id': request.user.id,
        'name': request.user.name,
        'email': request.user.email,
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
    absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
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
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

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

            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://'+current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                absurl+"?redirect_url="+redirect_url                        
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