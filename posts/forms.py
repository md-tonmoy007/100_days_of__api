from django.forms import ModelForm

from .models import Post, PostAttachment, Project


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('body',)


class AttachmentForm(ModelForm):
    class Meta:
        model = PostAttachment
        fields = ('image',)


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description')


