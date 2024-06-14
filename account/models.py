from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import random
# from posts.models import Project
from django.db import models

# Create your models here.
class CustomUserManager(UserManager):
    def _create_user(self, name, email, password, **extra_fields):
        if not email:
            raise ValueError("You have not provided a valid e-mail address")
        
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_user(self, name=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(name, email, password, **extra_fields)
    
    def create_superuser(self, name="admin", email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(name, email, password, **extra_fields)
    
    
    
AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google',
                  'twitter': 'twitter', 'email': 'email'}


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, default='')
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True)
    friends = models.ManyToManyField('self')
    friends_count = models.IntegerField(default=0)

    people_you_may_know = models.ManyToManyField('self')

    posts_count = models.IntegerField(default=0)
    
    is_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    project = models.ForeignKey('posts.Project', related_name='user', on_delete=models.CASCADE, null=True, blank=True)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('email'))
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
    def get_avatar(self):
        id = random.randint(0, 600)
        if self.avatar:
            return settings.WEBSITE_URL + self.avatar.url
        else:
            return f'https://picsum.photos/400/400'