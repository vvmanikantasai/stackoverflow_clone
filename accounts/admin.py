from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, ReputationHistory, Follow


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = [
        'avatar',
        'bio',
        'reputation',
        'website',
        'github_url',
        'x_url',
        'location',
    ]


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_reputation']

    def get_reputation(self, obj):
        try:
            return obj.profile.reputation
        except:
            return 0
    get_reputation.short_description = 'Reputation'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(ReputationHistory)
admin.site.register(Follow)
