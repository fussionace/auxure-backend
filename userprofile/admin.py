from django.contrib import admin

from .models import UserProfile

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'profile_picture', 'shipping_address', 'billing_address', 'email']

admin.site.register(UserProfile, UserProfileAdmin)
