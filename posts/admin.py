from django.contrib import admin

# Register your models here.
from .models import  *

admin.site.register(Post)
admin.site.register(PostAttachment)
admin.site.register(Comment)
admin.site.register(Project)
admin.site.register(Like)