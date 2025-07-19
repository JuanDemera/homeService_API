
from django.apps import AppConfig

class CartsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users.carts'

    def ready(self):
        import users.carts.signals