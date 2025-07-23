from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

@api_view(['GET'])
def test_connection(request):
    return Response({'status': 'ok', 'message': 'Conexión exitosa'})

class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

def post(self, request, *args, **kwargs):
        print("📥 Datos recibidos en login:", request.data)

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print("❌ Error en validación:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token_data = serializer.validated_data
        print("✅ Datos validados:", token_data)

        return Response(token_data, status=status.HTTP_200_OK)
