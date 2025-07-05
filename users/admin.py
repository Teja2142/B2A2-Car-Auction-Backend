from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import messages
from django.db import IntegrityError, transaction
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'mobile', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'mobile')
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('mobile',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('mobile',)}),
    )

    def save_model(self, request, obj, form, change):
        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)
        except IntegrityError as e:
            if 'unique' in str(e).lower() and 'mobile' in str(e).lower():
                self.message_user(request, 'A user with this mobile already exists.', level=messages.ERROR)
            else:
                self.message_user(request, f'Error: {e}', level=messages.ERROR)

admin.site.site_header = "B2A2 Car Auction Admin Portal"
admin.site.site_title = "B2A2 Car Auction | Admin Panel"
admin.site.index_title = "Welcome to the B2A2 Car Auction Management Dashboard"
admin.site.site_url = "/"  
admin.site.empty_value_display = "(None)"
admin.site.enable_nav_sidebar = True
