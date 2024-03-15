from django.contrib.auth.forms import UserCreationForm
from rest_framework import serializers
from django import forms
from django.contrib import auth
from .models import User
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'name', 'password1', 'password2')
        
        
        

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'access': user.tokens()['access'],
            'refresh': user.tokens()['refresh']
            
        }

    class Meta:
        model = User
        fields = ['email', 'password', 'token']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        print(email, password)
        filtered_user_by_email = User.objects.filter(email=email)
        user = auth.authenticate(email=email, password=password)

        if filtered_user_by_email.exists() and filtered_user_by_email[0].auth_provider != 'email':
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')

        return {
            'email': user.email,
            'name': user.name,
            'token': user.tokens,
        }
        
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'name', 'avatar',)