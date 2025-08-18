from django.db import models
from django.core.exceptions import ValidationError
from core.models import User

class Address(models.Model):
    """Modelo para almacenar direcciones de usuarios"""
    
    # Relación con usuario
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='addresses'
    )
    
    # Información básica
    title = models.CharField(
        max_length=100, 
        help_text="Ej: Casa, Trabajo, Oficina, etc.",
        null=True,
        blank=True
    )
    
    # Dirección detallada (todos nullables para no romper BD)
    street = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        help_text="Calle y número"
    )
    city = models.CharField(
        max_length=100, 
        null=True, 
        blank=True
    )
    state = models.CharField(
        max_length=100, 
        null=True, 
        blank=True
    )
    postal_code = models.CharField(
        max_length=10, 
        null=True, 
        blank=True
    )
    country = models.CharField(
        max_length=100, 
        default="Ecuador",
        null=True,
        blank=True,
        help_text="Solo se permiten direcciones de Ecuador"
    )
    
    # Coordenadas geográficas (capturadas por geolocalización)
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Latitud capturada por geolocalización"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Longitud capturada por geolocalización"
    )
    
    # Dirección formateada (para mostrar)
    formatted_address = models.TextField(
        null=True, 
        blank=True,
        help_text="Dirección completa formateada"
    )
    
    # Configuración
    is_default = models.BooleanField(
        default=False,
        help_text="Dirección principal del usuario"
    )
    is_active = models.BooleanField(
        default=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_default']),
            models.Index(fields=['is_active']),
        ]

    def clean(self):
        """Validar límites de direcciones por tipo de usuario y país"""
        # Validar que sea Ecuador
        if self.country and self.country.lower() not in ['ecuador', 'ec']:
            raise ValidationError(
                "Solo se permiten direcciones de Ecuador."
            )
        
        if self.pk is None:  # Solo para nuevas direcciones
            user_addresses_count = Address.objects.filter(
                user=self.user, 
                is_active=True
            ).count()
            
            if self.user.role == User.Role.CONSUMER and user_addresses_count >= 3:
                raise ValidationError(
                    "Los usuarios consumer pueden tener máximo 3 direcciones."
                )
            elif self.user.role == User.Role.PROVIDER and user_addresses_count >= 1:
                raise ValidationError(
                    "Los providers pueden tener máximo 1 dirección."
                )

    def save(self, *args, **kwargs):
        """Validar y guardar la dirección"""
        self.clean()
        
        # Si se marca como default, desmarcar otras
        if self.is_default:
            Address.objects.filter(
                user=self.user, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        # Generar dirección formateada si no existe
        if not self.formatted_address:
            self.formatted_address = self._generate_formatted_address()
        
        super().save(*args, **kwargs)

    def _generate_formatted_address(self):
        """Generar dirección formateada automáticamente"""
        parts = []
        
        if self.street:
            parts.append(self.street)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country:
            parts.append(self.country)
        
        return ", ".join(parts) if parts else "Dirección sin especificar"

    def __str__(self):
        title = self.title or "Sin título"
        return f"{title} - {self.user.username}"

    @property
    def coordinates(self):
        """Obtener coordenadas como tupla"""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None

    @property
    def has_coordinates(self):
        """Verificar si tiene coordenadas"""
        return self.latitude is not None and self.longitude is not None
