from django.contrib import admin
from django.utils.html import format_html
from .models import Vehicle, VehicleImage

class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1
    fields = ('image', 'image_preview')
    readonly_fields = ('image_preview',)
    show_change_link = True

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px;" />', obj.image.url)
        return "(No image)"
    image_preview.short_description = "Preview"

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'vin', 'make', 'model', 'year', 'color', 'mileage', 'dealer', 'status', 'starting_price')
    search_fields = ('vin', 'make', 'model', 'dealer__company_name')
    list_filter = ('year', 'make', 'model', 'status', 'dealer')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [VehicleImageInline]

@admin.register(VehicleImage)
class VehicleImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'image', 'image_preview')
    search_fields = ('vehicle__vin', 'vehicle__make', 'vehicle__model')
    list_filter = ('vehicle__make', 'vehicle__model')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px;" />', obj.image.url)
        return "(No image)"
    image_preview.short_description = "Preview"
