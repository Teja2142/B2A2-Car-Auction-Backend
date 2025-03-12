from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'mobile')
    search_fields = ('name', 'email', 'mobile')



admin.site.site_header = "B2A2 Car Auction Admin"
admin.site.site_title = "B2A2 Car Auction Admin Panel"
admin.site.index_title = "Welcome to B2A2 Car Auction Admin"
