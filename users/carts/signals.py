from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import User
from .models import Cart

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    """
    Crea automáticamente un carrito para nuevos usuarios guest o consumer
    """
    if created and instance.role in [User.Role.GUEST, User.Role.CONSUMER]:
        Cart.objects.create(user=instance)