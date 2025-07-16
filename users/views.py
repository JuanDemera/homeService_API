from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from core.models import User
from .serializers import GuestSerializer, RegisterConsumerSerializer
from .utils.otp import generate_otp

@method_decorator([never_cache, csrf_protect], name='dispatch')
class GuestAccessView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        with transaction.atomic():
            last_guest = User.objects.filter(role=User.Role.GUEST).order_by('-id').first()
            count = int(last_guest.username.replace('guest', '')) + 1 if last_guest else 1
            username = f'guest{count:04d}'
            
            user = User.objects.create_user(
                username=username,
                phone=f'guest{count:04d}',
                password='guestpass',
                role=User.Role.GUEST
            )
            
            return Response(
                GuestSerializer(user).data, 
                status=status.HTTP_201_CREATED
            )

class SendOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response(
                {'error': 'El teléfono es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        otp = generate_otp()
        cache_key = f'otp_{phone}'
        
        if cache.get(cache_key):
            return Response(
                {'error': 'Ya se ha enviado un código. Intenta más tarde.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        cache.set(cache_key, otp, timeout=300)
        return Response(
            {'otp': otp, 'expires_in': 300}, 
            status=status.HTTP_200_OK
        )

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone = request.data.get('phone')
        otp_input = request.data.get('otp')
        otp_real = cache.get(f'otp_{phone}')

        if not all([phone, otp_input]):
            return Response(
                {'error': 'Teléfono y OTP son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_input != otp_real:
            return Response(
                {'error': 'OTP inválido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(phone=phone)
            if user.role != User.Role.GUEST:
                return Response(
                    {'error': 'Solo usuarios guest pueden verificarse'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            user.is_verified = True
            user.role = User.Role.CONSUMER
            user.save()
            
            cache.delete(f'otp_{phone}')
            
            return Response(
                {'message': 'Usuario verificado correctamente'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class RegisterConsumerView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterConsumerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Usuario registrado correctamente'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)