from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'mobile', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'mobile')



admin.site.site_header = "B2A2 Car Auction Admin"
admin.site.site_title = "B2A2 Car Auction Admin Panel"
admin.site.index_title = "Welcome to B2A2 Car Auction Admin"
