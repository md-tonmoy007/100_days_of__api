from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User, FriendshipRequest

class CustomUserChangeForm(UserChangeForm):
	class Meta(UserChangeForm.Meta):
		model = User

class CustomUserCreationForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		model = User
		fields = ('email', 'name')

class UserAdmin(BaseUserAdmin):
	form = CustomUserChangeForm
	add_form = CustomUserCreationForm
	model = User
	list_display = ('email', 'name', 'is_staff', 'is_superuser', 'is_active')
	list_filter = ('is_staff', 'is_superuser', 'is_active')
	fieldsets = (
		(None, {'fields': ('email', 'password')}),
		('Personal info', {'fields': ('name', 'avatar')}),
		('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		('Important dates', {'fields': ('last_login', 'date_joined')}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'name', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active')
		}),
	)
	search_fields = ('email', 'name')
	ordering = ('email',)
	filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(User, UserAdmin)
admin.site.register(FriendshipRequest)