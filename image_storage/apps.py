from django.apps import AppConfig


class ImageStorageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'image_storage'
    verbose_name = 'Almacenamiento de Imágenes'
    
    def ready(self):
        """Configuración que se ejecuta cuando la aplicación está lista"""
        import image_storage.signals  # Importar señales si las hay
