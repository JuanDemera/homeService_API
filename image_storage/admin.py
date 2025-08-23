from django.contrib import admin
from .models import UserProfileImage, ServiceImage, ImageUploadLog

# Constantes para el admin
FILE_SIZE_DISPLAY_LABEL = "Tamaño"

@admin.register(UserProfileImage)
class UserProfileImageAdmin(admin.ModelAdmin):
    list_display = ['user', 'image_preview', 'file_size_display', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />'
        return "Sin imagen"
    image_preview.short_description = "Vista previa"
    image_preview.allow_tags = True
    
    def file_size_display(self, obj):
        if obj.image and hasattr(obj.image, 'size'):
            size_kb = obj.image.size / 1024
            if size_kb > 1024:
                return f"{size_kb/1024:.1f} MB"
            return f"{size_kb:.1f} KB"
        return "N/A"
    file_size_display.short_description = FILE_SIZE_DISPLAY_LABEL

@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ['service_id', 'image_preview', 'is_primary', 'file_size_display', 'created_at', 'is_active']
    list_filter = ['is_primary', 'is_active', 'created_at']
    search_fields = ['service_id']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    list_editable = ['is_primary']
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />'
        return "Sin imagen"
    image_preview.short_description = "Vista previa"
    image_preview.allow_tags = True
    
    def file_size_display(self, obj):
        if obj.image and hasattr(obj.image, 'size'):
            size_kb = obj.image.size / 1024
            if size_kb > 1024:
                return f"{size_kb/1024:.1f} MB"
            return f"{size_kb:.1f} KB"
        return "N/A"
    file_size_display.short_description = FILE_SIZE_DISPLAY_LABEL

@admin.register(ImageUploadLog)
class ImageUploadLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'upload_type', 'file_name', 'file_size_display', 'success', 'created_at']
    list_filter = ['upload_type', 'success', 'created_at']
    search_fields = ['user__username', 'user__email', 'file_name']
    readonly_fields = ['created_at']
    list_editable = ['success']
    
    def file_size_display(self, obj):
        if obj.file_size:
            size_kb = obj.file_size / 1024
            if size_kb > 1024:
                return f"{size_kb/1024:.1f} MB"
            return f"{size_kb:.1f} KB"
        return "N/A"
    file_size_display.short_description = FILE_SIZE_DISPLAY_LABEL
