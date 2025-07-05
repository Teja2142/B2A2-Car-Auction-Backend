from django.contrib import admin
from .models import DealerProfile

@admin.register(DealerProfile)
class DealerProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'company_name', 'address', 'city', 'state', 'country', 'phone', 'created_at')
    search_fields = ('company_name', 'user__email', 'user__username')
    list_filter = ('city', 'state', 'country')
    readonly_fields = ('created_at',)
