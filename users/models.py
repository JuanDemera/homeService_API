from django.db import models
from django.utils import timezone
from core.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(db_index=True)
    cedula = models.CharField(
        max_length=20, 
        unique=True, 
        null=True, 
        blank=True,
        db_index=True
    )
    birth_date = models.DateField()
    edad = models.IntegerField(blank=True, null=True)
    photo = models.URLField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['cedula']),
        ]

    def save(self, *args, **kwargs):
        if self.birth_date:
            today = timezone.now().date()
            self.edad = today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"