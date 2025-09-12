from django.urls import path
from . import api

urlpatterns = [
    # Post endpoints
    path('', api.post_list, name='post_list'),
    path('post/<str:pk>/', api.post_detail, name='post_detail'),
    path('create/', api.post_create, name='post_create'),
    path('<str:pk>/like/', api.post_like, name='post_like'),
    path('<uuid:pk>/delete/', api.post_delete, name='post_delete'),
    path('<str:pk>/comment/', api.post_create_comment, name='post_create_comment'),
    path('<str:pk>/comment_show/', api.comment_show, name='comment_show'),
    
    # Thread endpoints
    path('threads/', api.thread_list, name='thread_list'),
    path('threads/create/', api.thread_create, name='thread_create'),
    path('threads/join/', api.thread_join, name='thread_join'),
    path('threads/my/', api.user_threads, name='user_threads'),
    path('threads/<str:pk>/', api.thread_detail, name='thread_detail'),
]