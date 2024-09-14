from django.urls import path
from . import api
import uuid

urlpatterns = [
    path('', api.post_list, name='post_list'),
    path('post/<str:pk>/', api.post_detail, name='post_detail'),
    
    path('create/', api.post_create, name='post_create'),
    path('<str:pk>/like/', api.post_like, name='post_like'),
    path('<uuid:pk>/delete/', api.post_delete, name='post_delete'),
    path('<str:pk>/comment/', api.post_create_comment, name='post_create_comment'),
    path('<str:pk>/comment_show/', api.comment_show, name='comment_show'),
    path('project/create/', api.project_create, name='project create'),
    path('trending/', api.trending, name='trending'),
]