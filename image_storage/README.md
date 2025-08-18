# Servicio de Almacenamiento de Imágenes

Este módulo proporciona funcionalidades completas para el almacenamiento y gestión de imágenes en la aplicación HomeService API.

## Características

- **Imágenes de Perfil de Usuarios**: Gestión de fotos de perfil con validación y optimización
- **Imágenes de Servicios**: Múltiples imágenes por servicio con imagen principal
- **Subida Múltiple**: Soporte para subir varias imágenes a la vez
- **Validación Avanzada**: Validación de formato, tamaño y dimensiones
- **Optimización Automática**: Redimensionamiento y compresión automática
- **Logs de Actividad**: Registro de todas las subidas y errores
- **Gestión de Permisos**: Control de acceso basado en propiedad de recursos

## Modelos

### UserProfileImage
- Almacena la imagen de perfil de cada usuario
- Relación uno a uno con el modelo User
- Validación de formato y tamaño (máximo 5MB)

### ServiceImage
- Almacena múltiples imágenes por servicio
- Soporte para imagen principal
- Validación de formato y tamaño (máximo 10MB)

### ImageUploadLog
- Registra todas las operaciones de subida
- Incluye información de éxito/error
- Útil para auditoría y debugging

## APIs Disponibles

### Imágenes de Perfil

#### GET /api/images/profile/
Obtener la imagen de perfil del usuario autenticado

#### POST /api/images/profile/
Subir o actualizar imagen de perfil

#### PUT /api/images/profile/
Actualizar imagen de perfil

#### DELETE /api/images/profile/
Eliminar imagen de perfil

### Imágenes de Servicios

#### GET /api/images/services/{service_id}/images/
Listar todas las imágenes de un servicio

#### POST /api/images/services/{service_id}/images/
Subir nueva imagen para un servicio

#### GET /api/images/services/{service_id}/images/summary/
Obtener resumen de imágenes de un servicio

#### GET /api/images/services/images/{image_id}/
Obtener detalles de una imagen específica

#### PUT /api/images/services/images/{image_id}/
Actualizar una imagen específica

#### DELETE /api/images/services/images/{image_id}/
Eliminar una imagen específica

#### POST /api/images/services/images/{image_id}/set-primary/
Establecer una imagen como principal

### Subida Múltiple

#### POST /api/images/services/bulk-upload/
Subir múltiples imágenes para un servicio (máximo 10)

### Logs

#### GET /api/images/logs/
Obtener logs de subida del usuario autenticado

## Validaciones

### Imágenes de Perfil
- **Formatos permitidos**: JPG, JPEG, PNG, WEBP
- **Tamaño máximo**: 5MB
- **Dimensiones mínimas**: 100x100 píxeles
- **Dimensiones máximas**: 2048x2048 píxeles

### Imágenes de Servicios
- **Formatos permitidos**: JPG, JPEG, PNG, WEBP
- **Tamaño máximo**: 10MB
- **Dimensiones mínimas**: 200x200 píxeles
- **Dimensiones máximas**: 4096x4096 píxeles

## Servicios

### ImageProcessingService
- `resize_image()`: Redimensionar y optimizar imágenes
- `create_thumbnail()`: Crear miniaturas
- `validate_image_format()`: Validar formato de imagen

### ImageStorageService
- `get_storage_path()`: Generar rutas de almacenamiento
- `cleanup_old_images()`: Limpiar imágenes antiguas
- `get_image_url()`: Obtener URLs completas

### ImageValidationService
- `validate_profile_image()`: Validar imágenes de perfil
- `validate_service_image()`: Validar imágenes de servicio

## Uso

### Subir Imagen de Perfil

```python
import requests

# Subir imagen de perfil
with open('profile.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post(
        'http://localhost:8000/api/images/profile/',
        files=files,
        headers={'Authorization': 'Bearer YOUR_TOKEN'}
    )
```

### Subir Imagen de Servicio

```python
# Subir imagen para un servicio
with open('service.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post(
        'http://localhost:8000/api/images/services/1/images/',
        files=files,
        headers={'Authorization': 'Bearer YOUR_TOKEN'}
    )
```

### Subida Múltiple

```python
# Subir múltiples imágenes
files = []
for i in range(3):
    with open(f'image_{i}.jpg', 'rb') as f:
        files.append(('images', f))

data = {'service_id': 1}
response = requests.post(
    'http://localhost:8000/api/images/services/bulk-upload/',
    files=files,
    data=data,
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
```

## Configuración

### Settings.py
Asegúrate de tener configurado:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### URLs
Las URLs ya están incluidas en el archivo principal:

```python
path('api/images/', include('image_storage.urls')),
```

## Tests

Ejecutar los tests:

```bash
python manage.py test image_storage
```

Los tests cubren:
- Creación y validación de modelos
- APIs de subida y gestión
- Validación de imágenes
- Procesamiento de imágenes

## 🔐 Seguridad

### Autenticación y Autorización
- **Autenticación requerida**: Todas las operaciones requieren JWT Token
- **Verificación de permisos**: Solo los propietarios pueden modificar sus recursos
- **Validación de archivos**: Verificación de tipo, contenido y tamaño
- **Limpieza automática**: Eliminación de archivos físicos al borrar registros

## 📋 Manejo de Casos Sin Imágenes

### ✅ Casos Soportados
- **Usuario sin imagen de perfil**: Retorna mensaje informativo y `has_image: false`
- **Servicio sin imágenes**: Retorna lista vacía y `has_images: false`
- **Primera subida de imagen**: Crea registro automáticamente
- **Actualización de imagen**: Reemplaza imagen existente
- **Eliminación de imagen inexistente**: Retorna 404 con mensaje apropiado

### 📝 Respuestas para Casos Sin Imágenes

#### Usuario Sin Imagen de Perfil
```json
{
    "message": "No hay imagen de perfil configurada",
    "has_image": false,
    "image_url": null,
    "file_size": 0
}
```

#### Servicio Sin Imágenes
```json
{
    "message": "No hay imágenes configuradas para este servicio",
    "total_images": 0,
    "images": [],
    "has_images": false
}
```

#### Resumen de Servicio Sin Imágenes
```json
{
    "service_id": 1,
    "service_name": "Mi Servicio",
    "total_images": 0,
    "primary_image": null,
    "all_images": [],
    "has_images": false,
    "message": "No hay imágenes configuradas para este servicio"
}
```

### Permisos por Tipo de Usuario

#### 👤 Usuario Regular
- ✅ Subir/editar/eliminar su propia imagen de perfil
- ✅ Ver sus propios logs de subida
- ✅ Ver imágenes de servicios (solo lectura)
- ❌ Modificar imágenes de otros usuarios
- ❌ Subir imágenes para servicios que no posee

#### 🏢 Provider (Proveedor de Servicios)
- ✅ Todo lo que puede un usuario regular
- ✅ Subir/editar/eliminar imágenes de sus propios servicios
- ✅ Establecer imagen principal para sus servicios
- ✅ Subida múltiple de imágenes para sus servicios
- ✅ Ver resumen de imágenes de sus servicios
- ❌ Modificar imágenes de servicios de otros providers

### Verificaciones de Seguridad Implementadas
- **Verificación de propiedad de servicio**: `service.provider.user == request.user`
- **Verificación de propiedad de perfil**: `obj.user == request.user`
- **Validación de tokens JWT**: En cada request
- **Validación de archivos**: Tipo, tamaño y contenido
- **Logs de auditoría**: Todas las operaciones se registran

📖 **Documentación completa de seguridad**: Ver [SECURITY.md](SECURITY.md)

## Mantenimiento

### Limpieza de Archivos
Los archivos se eliminan automáticamente cuando se borran los registros correspondientes.

### Logs
Los logs se mantienen para auditoría. Considera implementar una tarea programada para limpiar logs antiguos.

### Optimización
El servicio incluye optimización automática de imágenes para mejorar el rendimiento. 