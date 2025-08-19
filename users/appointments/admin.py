from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'service', 
        'consumer', 
        'provider', 
        'appointment_date', 
        'appointment_time', 
        'status',
        'has_service_address'
    ]
    list_filter = [
        'status', 
        'is_temporary', 
        'payment_completed', 
        'appointment_date',
        'created_at'
    ]
    search_fields = [
        'consumer__username', 
        'provider__username', 
        'service__title',
        'service_address',
        'notes'
    ]
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'is_expired', 
        'time_until_expiry'
    ]
    list_editable = ['status']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('consumer', 'provider', 'service', 'status')
        }),
        ('Fecha y Hora', {
            'fields': ('appointment_date', 'appointment_time')
        }),
        ('Dirección del Servicio', {
            'fields': ('service_address', 'service_latitude', 'service_longitude'),
            'classes': ('collapse',)
        }),
        ('Notas y Comentarios', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Información de Pago', {
            'fields': ('is_temporary', 'payment_completed', 'payment_reference', 'expires_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_service_address(self, obj):
        """Indicar si el appointment tiene dirección"""
        return bool(obj.service_address)
    has_service_address.boolean = True
    has_service_address.short_description = 'Tiene Dirección'
