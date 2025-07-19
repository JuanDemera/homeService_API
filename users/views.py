from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.db import transaction
from core.models import User
from users.models import UserProfile
from users.serializers import GuestSerializer, RegisterConsumerSerializer
from .utils.otp import generate_otp
from datetime import date

class GuestAccessView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            with transaction.atomic():
                # Obtener el último ID de usuario guest
                last_guest = User.objects.filter(role=User.Role.GUEST).order_by('-id').first()
                count = (last_guest.id + 1) if last_guest else 1
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
                {
                    "status": "error",
                    "message": str(e),
                    "details": "Error al crear usuario guest"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class SendOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone = serializer.validated_data['phone']
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
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone = serializer.validated_data['phone']
        otp_input = serializer.validated_data['otp']
        otp_real = cache.get(f'otp_{phone}')

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
            user = serializer.save()
            return Response(
                {
                    'message': 'Usuario registrado correctamente',
                    'user_id': user.id
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)