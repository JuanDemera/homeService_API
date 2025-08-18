from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.cache import cache
from django.db import transaction
from core.models import User
from users.models import UserProfile
from users.serializers import (
    GuestSerializer, RegisterConsumerSerializer, ConsumerProfileSerializer,
    UpdateConsumerProfileSerializer, ChangePasswordSerializer
)
from .utils.otp import generate_otp
from datetime import date
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema

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
                
                # Generar tokens JWT
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                
                return Response(
                    {
                        "status": "success",
                        "user": GuestSerializer(user).data,
                        "tokens": {
                            "access": access_token,
                            "refresh": str(refresh)
                        },
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

    @swagger_auto_schema(
        request_body=RegisterConsumerSerializer,
        operation_description="Registra un nuevo usuario consumidor con los datos requeridos."
    )

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

# Vista para obtener el perfil del usuario consumer
class ConsumerProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene el perfil completo del usuario consumer autenticado."
    )
    def get(self, request):
        try:
            # Verificar que el usuario sea consumer
            if request.user.role != User.Role.CONSUMER:
                return Response(
                    {'error': 'Solo usuarios consumer pueden acceder a este endpoint'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Obtener el perfil del usuario
            profile = UserProfile.objects.get(user=request.user)
            serializer = ConsumerProfileSerializer(profile)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Perfil de usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al obtener el perfil: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Vista para actualizar el perfil del usuario consumer
class UpdateConsumerProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=UpdateConsumerProfileSerializer,
        operation_description="Actualiza el perfil del usuario consumer autenticado."
    )
    def put(self, request):
        try:
            # Verificar que el usuario sea consumer
            if request.user.role != User.Role.CONSUMER:
                return Response(
                    {'error': 'Solo usuarios consumer pueden acceder a este endpoint'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Obtener el perfil del usuario
            profile = UserProfile.objects.get(user=request.user)
            serializer = UpdateConsumerProfileSerializer(profile, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        'message': 'Perfil actualizado correctamente',
                        'data': ConsumerProfileSerializer(profile).data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Perfil de usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al actualizar el perfil: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Vista para cambiar la contraseña del usuario
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        operation_description="Cambia la contraseña del usuario autenticado."
    )
    def post(self, request):
        try:
            serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                user = request.user
                new_password = serializer.validated_data['new_password']
                
                # Cambiar la contraseña
                user.set_password(new_password)
                user.save()
                
                return Response(
                    {'message': 'Contraseña actualizada correctamente'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {'error': f'Error al cambiar la contraseña: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 