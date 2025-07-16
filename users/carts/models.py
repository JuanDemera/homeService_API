from django.db import models
from core.models import User
from providers.services.models import Service

class Cart(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Cart #{self.id} - {self.user.username}"

    @property
    def total_items(self):
        return self.items.count()

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    service = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'service')
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['service']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.service.title} in Cart #{self.cart.id}"

    @property
    def total_price(self):
        return self.service.price * self.quantity