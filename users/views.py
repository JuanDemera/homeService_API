from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from datetime import date
from django.core.cache import cache
from .serializers import (
    GuestSerializer,
    OTPSerializer,
    VerifyOTPSerializer,
    RegisterConsumerSerializer
)
from core.models import User
from users.models import UserProfile
from users.utils.otp import generate_otp

@method_decorator([never_cache, csrf_protect], name='dispatch')
class GuestAccessView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    serializer_class = None 

    def post(self, request):
        try:
            with transaction.atomic():
                last_guest = User.objects.filter(role=User.Role.GUEST).order_by('-id').first()
                count = int(last_guest.username.replace('guest', '')) + 1 if last_guest else 1
                username = f'guest{count:04d}'
                
                user = User.objects.create_user(
                    username=username,
                    phone=username,  
                    password='guestpass',
                    role=User.Role.GUEST
                )
                
                UserProfile.objects.create(
                    user=user,
                    firstname=f"Guest{count}",
                    lastname="Temp",
                    email=f"guest{count}@temp.com",
                    birth_date=date(2000, 1, 1),
                )
                
                return Response(
                    {
                        "status": "success",
                        "user": GuestSerializer(user).data,
                        "message": "Usuario guest creado correctamente"
                    },
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            return Response(
                {"status": "error", "message": "Error en el servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SendOTPView(APIView):
    permission_classes = [AllowAny]
    serializer_class = OTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Valida automáticamente (retorna 400 si falla)
        
        phone = serializer.validated_data['phone']
        cache_key = f'otp_{phone}'
        
        # Verifica si ya existe un OTP activo
        if cache.get(cache_key):
            return Response(
                {'error': 'Ya se ha enviado un código. Espera 5 minutos.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Genera y almacena el OTP
        otp = generate_otp()  # Usamos tu función
        cache.set(cache_key, otp, timeout=300)  # 5 minutos de expiración
        
        # En producción, aquí iría el envío real por SMS/Email
        print(f"OTP para {phone}: {otp}")  # Solo para desarrollo
        
        return Response(
            {'message': 'Código OTP enviado', 'expires_in': 300},
            status=status.HTTP_200_OK
        )

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone = serializer.validated_data['phone']
        otp_input = serializer.validated_data['otp']
        otp_real = cache.get(f'otp_{phone}')

        if otp_input != otp_real:
            return Response(
                {'error': 'Código OTP incorrecto o expirado'},
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
    serializer_class = RegisterConsumerSerializer 

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Usuario registrado correctamente'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)