from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class UsernameOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        user = User.objects.filter(username=username).first()
        if user is None:
            user = User.objects.filter(phone=username).first()
        if user and user.check_password(password):
            return user
        return None

AUTHENTICATION_BACKENDS = [
    'core.backends.UsernameOrPhoneBackend',
    'django.contrib.auth.backends.ModelBackend',
]