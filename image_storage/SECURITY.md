# Seguridad y Permisos - Servicio de Imágenes

## 🔐 Sistema de Autenticación y Autorización

El servicio de almacenamiento de imágenes implementa un sistema robusto de seguridad que garantiza que solo los usuarios autorizados puedan acceder y modificar sus recursos.

### Autenticación

**Todas las operaciones requieren autenticación mediante JWT Token:**

```bash
# Ejemplo de header de autorización
Authorization: Bearer <tu_jwt_token>
```

### Permisos por Tipo de Usuario

#### 👤 Usuario Regular
- **Puede hacer:**
  - Subir/editar/eliminar su propia imagen de perfil
  - Ver sus propios logs de subida
  - Ver imágenes de servicios (solo lectura)

- **No puede hacer:**
  - Modificar imágenes de otros usuarios
  - Subir imágenes para servicios que no posee
  - Acceder a logs de otros usuarios

#### 🏢 Provider (Proveedor de Servicios)
- **Puede hacer:**
  - Todo lo que puede un usuario regular
  - Subir/editar/eliminar imágenes de sus propios servicios
  - Establecer imagen principal para sus servicios
  - Subida múltiple de imágenes para sus servicios
  - Ver resumen de imágenes de sus servicios

- **No puede hacer:**
  - Modificar imágenes de servicios de otros providers
  - Acceder a información de otros providers

## 🛡️ Permisos Implementados

### 1. IsProfileOwner
```python
# Solo el propietario puede modificar su imagen de perfil
permission_classes = [IsProfileOwner]
```

**Aplicado en:**
- `UserProfileImageView` - Gestión de imagen de perfil

### 2. IsServiceOwner
```python
# Solo el propietario del servicio puede modificar sus imágenes
permission_classes = [IsServiceOwner]
```

**Aplicado en:**
- `ServiceImageDetailView` - Gestión de imagen específica de servicio

### 3. CanManageServiceImages
```python
# Solo el propietario del servicio puede gestionar sus imágenes
permission_classes = [CanManageServiceImages]
```

**Aplicado en:**
- `ServiceImageListCreateView` - Listar y crear imágenes de servicios
- `BulkImageUploadView` - Subida múltiple de imágenes

## 🔍 Verificaciones de Seguridad

### Verificación de Propiedad de Servicio
```python
# En cada operación de servicio se verifica:
if service.provider.user != request.user:
    raise PermissionDenied("No tienes permisos para modificar este servicio.")
```

### Verificación de Propiedad de Perfil
```python
# En operaciones de perfil se verifica:
if obj.user != request.user:
    return False  # No tiene permisos
```

### Verificación de Autenticación
```python
# Todas las vistas verifican autenticación:
permission_classes = [IsAuthenticated]
```

## 📋 Matriz de Permisos

| Operación | Usuario Regular | Provider (Propio) | Provider (Otro) |
|-----------|----------------|-------------------|-----------------|
| **Imagen de Perfil** |
| Ver propia | ✅ | ✅ | ❌ |
| Editar propia | ✅ | ✅ | ❌ |
| Eliminar propia | ✅ | ✅ | ❌ |
| **Imágenes de Servicios** |
| Ver servicios | ✅ | ✅ | ✅ |
| Subir a servicio propio | ❌ | ✅ | ❌ |
| Editar servicio propio | ❌ | ✅ | ❌ |
| Eliminar servicio propio | ❌ | ✅ | ❌ |
| **Subida Múltiple** |
| Servicios propios | ❌ | ✅ | ❌ |
| **Logs** |
| Ver propios | ✅ | ✅ | ❌ |

## 🚨 Respuestas de Error

### Error de Autenticación (401)
```json
{
    "detail": "Las credenciales de autenticación no se proveyeron."
}
```

### Error de Permisos (403)
```json
{
    "detail": "No tienes permisos para modificar este servicio."
}
```

### Error de Recurso No Encontrado (404)
```json
{
    "detail": "No encontrado."
}
```

## 🔧 Configuración de Seguridad

### Headers de Seguridad
```python
# En settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Validación de Archivos
- Verificación de tipo MIME
- Validación de extensión
- Verificación de contenido de imagen
- Límites de tamaño

### Logs de Seguridad
```python
# Todas las operaciones se registran en ImageUploadLog
{
    "user": "usuario_id",
    "upload_type": "profile|service",
    "file_name": "archivo.jpg",
    "file_size": 1024,
    "success": true,
    "error_message": null,
    "created_at": "2024-01-01T00:00:00Z"
}
```

## 🧪 Testing de Seguridad

### Tests de Permisos
```bash
# Ejecutar tests de seguridad
python manage.py test image_storage.tests.ImageStorageAPITest
```

### Casos de Prueba Cubiertos
- ✅ Usuario no autenticado no puede acceder
- ✅ Usuario no puede modificar imagen de perfil de otro
- ✅ Provider no puede modificar servicios de otro
- ✅ Verificación de propiedad en todas las operaciones
- ✅ Validación de tokens JWT

## 🔄 Flujo de Autenticación

1. **Cliente envía request con JWT Token**
2. **Django verifica token y extrae usuario**
3. **Sistema verifica permisos específicos**
4. **Si tiene permisos → Ejecuta operación**
5. **Si no tiene permisos → Retorna 403**

## 📝 Ejemplos de Uso Seguro

### Subir Imagen de Perfil (Usuario Autenticado)
```bash
curl -X POST \
  -H "Authorization: Bearer <tu_token>" \
  -F "image=@profile.jpg" \
  http://localhost:8000/api/images/profile/
```

### Subir Imagen de Servicio (Provider)
```bash
curl -X POST \
  -H "Authorization: Bearer <token_provider>" \
  -F "image=@service.jpg" \
  http://localhost:8000/api/images/services/1/images/
```

### Verificar Permisos Antes de Operación
```python
# El sistema automáticamente verifica:
# 1. Que el usuario esté autenticado
# 2. Que sea propietario del recurso
# 3. Que tenga permisos para la operación
```

## ⚠️ Consideraciones de Seguridad

1. **Nunca exponer tokens en logs**
2. **Usar HTTPS en producción**
3. **Implementar rate limiting**
4. **Validar archivos en el frontend y backend**
5. **Mantener logs de auditoría**
6. **Revisar permisos regularmente**

## 🔒 Mejores Prácticas

- ✅ Siempre usar HTTPS
- ✅ Validar tokens en cada request
- ✅ Implementar rate limiting
- ✅ Logging de todas las operaciones
- ✅ Validación de archivos robusta
- ✅ Verificación de permisos en cada operación
- ✅ Respuestas de error genéricas (no exponer información sensible) 