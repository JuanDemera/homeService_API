from django.contrib import admin
from .models import Address

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'title', 'city', 'state', 'is_default', 
        'has_coordinates', 'is_active', 'created_at'
    ]
    list_filter = ['is_default', 'is_active', 'country', 'created_at']
    search_fields = [
        'user__username', 'user__phone', 'title', 'street', 
        'city', 'state', 'formatted_address'
    ]
    readonly_fields = ['created_at', 'updated_at', 'formatted_address']
    list_editable = ['is_default', 'is_active']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user',)
        }),
        ('Información de la Dirección', {
            'fields': ('title', 'street', 'city', 'state', 'postal_code', 'country')
        }),
        ('Geolocalización', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('is_default', 'is_active', 'formatted_address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_coordinates(self, obj):
        return obj.has_coordinates
    has_coordinates.boolean = True
    has_coordinates.short_description = 'Tiene Coordenadas'
