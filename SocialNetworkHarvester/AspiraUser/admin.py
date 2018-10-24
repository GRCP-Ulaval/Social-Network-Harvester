from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User

from AspiraUser.models import UserProfile

admin.site.unregister(Group)


@admin.register(UserProfile)
class UserProfileManager(admin.ModelAdmin):
    readonly_fields = (
        'twitter_app_valid',
        'facebook_app_valid',
        'youtube_app_valid'
    )
    list_display = (
        '__str__',
        'twitter_app_valid',
        'facebook_app_valid',
        'youtube_app_valid',
    )
    fieldsets = (
        ('', {
            'fields': (
                'user',
            ),
        }),
    )


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_superuser',
        'last_login'
    )
