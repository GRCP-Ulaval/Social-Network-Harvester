from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User

from AspiraUser.models import UserProfile

admin.site.unregister(Group)


@admin.register(UserProfile)
class UserProfileManager(admin.ModelAdmin):
    raw_id_fields = (
        'twitterUsersToHarvest',
        'twitterHashtagsToHarvest',
        'ytChannelsToHarvest',
        'ytPlaylistsToHarvest',
        'facebookPagesToHarvest'
    )
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
        ('Twitter app', {
            'classes': ('collapse', 'closed'),
            'fields': (
                ('twitterApp_consumerKey', 'twitterApp_consumer_secret'),
                ('twitterApp_access_token_key', 'twitterApp_access_token_secret'),
                'twitter_app_valid',
                ('twitterUsersToHarvest', 'twitterUsersToHarvestLimit'),
                ('twitterHashtagsToHarvest', 'twitterHashtagsToHarvestLimit'),
            ),
        }),
        ('Facebook app', {
            'classes': ('collapse', 'closed'),
            'fields': (
                ('facebookPagesToHarvest', 'facebookPagesToHarvestLimit'),
                'facebook_app_valid',
            ),
        }),
        ('Youtube app', {
            'classes': ('collapse', 'closed'),
            'fields': (
                'youtubeApp_dev_key',
                'youtube_app_valid',
                ('ytChannelsToHarvest', 'ytChannelsToHarvestLimit'),
                ('ytPlaylistsToHarvest', 'ytPlaylistsToHarvestLimit'),
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
