# 📋 Manejo de Casos Sin Imágenes

## 🎯 Propósito

Este documento describe cómo el sistema maneja los casos donde usuarios o servicios no tienen imágenes definidas desde el inicio, evitando errores y proporcionando respuestas informativas.

## ✅ Casos Soportados

### 1. Usuario Sin Imagen de Perfil
- **Situación**: Usuario recién registrado o que nunca ha subido imagen
- **Comportamiento**: Retorna respuesta informativa sin error
- **Estado**: `has_image: false`

### 2. Servicio Sin Imágenes
- **Situación**: Servicio recién creado sin imágenes
- **Comportamiento**: Retorna lista vacía con mensaje informativo
- **Estado**: `has_images: false`

### 3. Primera Subida de Imagen
- **Situación**: Primera vez que se sube una imagen
- **Comportamiento**: Crea registro automáticamente
- **Estado**: Transición de `false` a `true`

### 4. Actualización de Imagen Existente
- **Situación**: Reemplazar imagen existente
- **Comportamiento**: Actualiza registro y archivo
- **Estado**: Mantiene `true`

### 5. Eliminación de Imagen Inexistente
- **Situación**: Intentar eliminar imagen que no existe
- **Comportamiento**: Retorna 404 con mensaje apropiado
- **Estado**: Mantiene `false`

## 📝 Respuestas de API

### GET /api/images/profile/ (Sin Imagen)

```json
{
    "message": "No hay imagen de perfil configurada",
    "has_image": false,
    "image_url": null,
    "file_size": 0
}
```

**Código de Estado**: `200 OK`

### GET /api/images/services/{id}/images/ (Sin Imágenes)

```json
{
    "message": "No hay imágenes configuradas para este servicio",
    "total_images": 0,
    "images": [],
    "has_images": false
}
```

**Código de Estado**: `200 OK`

### GET /api/images/services/{id}/images/summary/ (Sin Imágenes)

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

**Código de Estado**: `200 OK`

### DELETE /api/images/profile/ (Sin Imagen)

```json
{
    "message": "No hay imagen de perfil para eliminar"
}
```

**Código de Estado**: `404 Not Found`

## 🔧 Implementación Técnica

### Vista de Perfil de Usuario

```python
def get_object(self):
    """Obtener la imagen de perfil del usuario actual"""
    try:
        return UserProfileImage.objects.get(user=self.request.user)
    except UserProfileImage.DoesNotExist:
        return None

def get(self, request, *args, **kwargs):
    """Obtener la imagen de perfil del usuario"""
    instance = self.get_object()
    if not instance or not instance.image:
        return Response({
            'message': 'No hay imagen de perfil configurada',
            'has_image': False,
            'image_url': None,
            'file_size': 0
        }, status=status.HTTP_200_OK)
```

### Vista de Imágenes de Servicio

```python
def list(self, request, *args, **kwargs):
    """Listar imágenes del servicio con manejo de caso vacío"""
    queryset = self.get_queryset()
    if not queryset.exists():
        return Response({
            'message': 'No hay imágenes configuradas para este servicio',
            'total_images': 0,
            'images': [],
            'has_images': False
        }, status=status.HTTP_200_OK)
```

### Serializers con Validación

```python
def get_image_url(self, obj):
    if obj and obj.image:
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url
    return None

def get_file_size(self, obj):
    if obj and obj.image and hasattr(obj.image, 'size'):
        return obj.image.size
    return 0
```

## 🧪 Tests de Validación

### Tests Implementados

```python
def test_user_without_profile_image(self):
    """Test: Usuario sin imagen de perfil"""
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertFalse(response.data['has_image'])
    self.assertIsNone(response.data['image_url'])
    self.assertEqual(response.data['file_size'], 0)

def test_service_without_images(self):
    """Test: Servicio sin imágenes"""
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertFalse(response.data['has_images'])
    self.assertEqual(response.data['total_images'], 0)
    self.assertEqual(response.data['images'], [])
```

### Ejecutar Tests

```bash
# Tests específicos para casos sin imágenes
python manage.py test image_storage.test_no_images

# Todos los tests
python manage.py test image_storage
```

## 🔄 Flujo de Estados

### Usuario Nuevo
1. **Estado inicial**: `has_image: false`
2. **Primera subida**: `has_image: true`
3. **Eliminación**: `has_image: false`

### Servicio Nuevo
1. **Estado inicial**: `has_images: false`
2. **Primera imagen**: `has_images: true`
3. **Eliminación de todas**: `has_images: false`

## 📊 Campos de Estado

### Para Imágenes de Perfil
- `has_image`: Boolean - Indica si hay imagen configurada
- `image_url`: String/Null - URL de la imagen (null si no existe)
- `file_size`: Integer - Tamaño del archivo (0 si no existe)

### Para Imágenes de Servicio
- `has_images`: Boolean - Indica si hay imágenes configuradas
- `total_images`: Integer - Número total de imágenes
- `images`: Array - Lista de imágenes (vacía si no hay)
- `primary_image`: Object/Null - Imagen principal (null si no hay)

## ⚠️ Consideraciones

### Frontend
- **Verificar `has_image`/`has_images`** antes de mostrar imágenes
- **Mostrar placeholder** cuando no hay imágenes
- **Manejar estados de carga** durante subidas
- **Validar respuestas** antes de actualizar UI

### Backend
- **No crear registros vacíos** automáticamente
- **Validar existencia** antes de operaciones
- **Manejar excepciones** graciosamente
- **Proporcionar mensajes informativos**

## 🎨 Ejemplos de Uso

### Verificar Si Hay Imagen de Perfil

```javascript
// Frontend
const response = await fetch('/api/images/profile/');
const data = await response.json();

if (data.has_image) {
    // Mostrar imagen
    showProfileImage(data.image_url);
} else {
    // Mostrar placeholder
    showDefaultAvatar();
}
```

### Verificar Si Hay Imágenes de Servicio

```javascript
// Frontend
const response = await fetch(`/api/images/services/${serviceId}/images/`);
const data = await response.json();

if (data.has_images) {
    // Mostrar galería
    showImageGallery(data.images);
} else {
    // Mostrar mensaje de no imágenes
    showNoImagesMessage(data.message);
}
```

### Subir Primera Imagen

```javascript
// Frontend
const formData = new FormData();
formData.append('image', file);

const response = await fetch('/api/images/profile/', {
    method: 'POST',
    body: formData,
    headers: {
        'Authorization': `Bearer ${token}`
    }
});

const data = await response.json();
if (response.ok) {
    // Actualizar UI
    updateProfileImage(data.image_url);
}
```

## 🔒 Seguridad

### Validaciones
- **Autenticación requerida** en todos los endpoints
- **Verificación de permisos** antes de operaciones
- **Validación de archivos** en subidas
- **Sanitización de respuestas** para evitar información sensible

### Logs
- **Registrar todas las operaciones** exitosas y fallidas
- **Incluir información de usuario** en logs
- **Mantener auditoría** de cambios de estado

---

**El sistema maneja graciosamente todos los casos donde no hay imágenes, proporcionando respuestas informativas y evitando errores.** 