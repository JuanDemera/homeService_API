# 🏠 Aplicación de Direcciones

## 📋 Descripción

La aplicación `addresses` permite a los usuarios (consumers y providers) gestionar sus direcciones con soporte para geolocalización y sugerencias de direcciones.

## 🎯 Características

### ✅ **Funcionalidades Principales**
- ✅ **Campos nullables**: No rompe la base de datos existente
- ✅ **Solo Ecuador**: Solo se permiten direcciones de Ecuador
- ✅ **Límites por usuario**: 
  - **Consumers**: Máximo 3 direcciones
  - **Providers**: Máximo 1 dirección
- ✅ **Geolocalización**: Captura automática de coordenadas (solo Ecuador)
- ✅ **Dirección manual**: Entrada manual con sugerencias de Ecuador
- ✅ **Dirección por defecto**: Una dirección principal por usuario
- ✅ **Validaciones**: Coordenadas válidas de Ecuador y límites de direcciones

### 🔧 **Tecnologías**
- Django REST Framework
- PostgreSQL (coordenadas geográficas)
- Geolocalización del navegador
- Sugerencias de direcciones (simuladas)

## 📊 Modelo de Datos

### **Address**
```python
{
    "id": 1,
    "user": "usuario_id",
    "title": "Casa",
    "street": "Av. Principal 123",
    "city": "Guayaquil",
    "state": "Guayas",
    "postal_code": "090101",
    "country": "Ecuador",
    "latitude": -2.1894,
    "longitude": -79.8891,
    "formatted_address": "Av. Principal 123, Guayaquil, Guayas, 090101, Ecuador",
    "is_default": true,
    "is_active": true,
    "created_at": "2025-01-18T10:00:00Z",
    "updated_at": "2025-01-18T10:00:00Z"
}
```

## 🚀 Endpoints

### **1. Listar Direcciones**
```http
GET /api/addresses/
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
    "total_addresses": 2,
    "addresses": [...],
    "has_addresses": true,
    "user_role": "consumer",
    "max_addresses": 3
}
```

### **2. Crear Dirección Manual**
```http
POST /api/addresses/
Authorization: Bearer <token>
Content-Type: application/json

{
    "title": "Casa",
    "street": "Av. Principal 123",
    "city": "Guayaquil",
    "state": "Guayas",
    "postal_code": "090101",
    "country": "Ecuador",
    "is_default": true
}
```

### **3. Crear Dirección con Geolocalización**
```http
POST /api/addresses/geolocation/
Authorization: Bearer <token>
Content-Type: application/json

{
    "title": "Mi ubicación actual",
    "latitude": -2.1894,
    "longitude": -79.8891,
    "is_default": true
}
```

### **4. Obtener Dirección por Defecto**
```http
GET /api/addresses/default/
Authorization: Bearer <token>
```

### **5. Establecer Dirección por Defecto**
```http
POST /api/addresses/{address_id}/set-default/
Authorization: Bearer <token>
```

### **6. Actualizar Dirección**
```http
PUT /api/addresses/{address_id}/
Authorization: Bearer <token>
Content-Type: application/json

{
    "title": "Casa actualizada",
    "street": "Nueva dirección 456"
}
```

### **7. Eliminar Dirección**
```http
DELETE /api/addresses/{address_id}/
Authorization: Bearer <token>
```

### **8. Sugerencias de Direcciones**
```http
GET /api/addresses/suggestions/?query=Av. Principal
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
    "predictions": [
        {
            "id": 1,
            "description": "Av. Principal, Guayaquil, Ecuador",
            "place_id": "place_1",
            "structured_formatting": {
                "main_text": "Av. Principal",
                "secondary_text": "Guayaquil, Ecuador"
            },
            "geometry": {
                "location": {
                    "lat": -2.1894,
                    "lng": -79.8891
                }
            }
        }
    ],
    "status": "OK"
}
```

### **9. Resumen de Direcciones**
```http
GET /api/addresses/summary/
Authorization: Bearer <token>
```

## 🔐 Permisos

### **CanManageAddresses**
- Solo usuarios `consumer` y `provider`
- Usuarios `admin` no pueden gestionar direcciones

### **IsAddressOwner**
- Solo el propietario puede gestionar sus direcciones
- Validación por JWT token

## 📱 Uso en Frontend

### **Geolocalización**
```javascript
// Obtener ubicación actual
navigator.geolocation.getCurrentPosition(
    (position) => {
        const { latitude, longitude } = position.coords;
        
        // Crear dirección con geolocalización
        fetch('/api/addresses/geolocation/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: 'Mi ubicación',
                latitude: latitude,
                longitude: longitude,
                is_default: true
            })
        });
    },
    (error) => {
        console.error('Error de geolocalización:', error);
    }
);
```

### **Sugerencias de Direcciones**
```javascript
// Buscar sugerencias
const searchAddress = async (query) => {
    const response = await fetch(`/api/addresses/suggestions/?query=${query}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    const data = await response.json();
    return data.predictions;
};
```

## ⚠️ Validaciones

### **Límites de Direcciones**
- **Consumer**: Máximo 3 direcciones activas
- **Provider**: Máximo 1 dirección activa

### **Coordenadas de Ecuador**
- **Latitud**: Entre -5.0 y 1.5 grados (rango de Ecuador)
- **Longitud**: Entre -81.5 y -75.0 grados (rango de Ecuador)

### **Campos Requeridos**
- Al menos coordenadas O dirección manual
- Solo direcciones de Ecuador
- Título opcional (se genera automáticamente)

## 🛠️ Configuración

### **Instalación**
```bash
# Las migraciones ya están aplicadas
python manage.py migrate addresses
```

### **Admin Django**
- Acceso completo a direcciones
- Filtros por usuario, estado, país
- Búsqueda por dirección y usuario

## 🔄 Flujo de Trabajo

1. **Usuario se registra** → Sin direcciones
2. **Agrega primera dirección** → Se marca como default
3. **Agrega más direcciones** → Hasta el límite según rol
4. **Cambia dirección default** → Se actualiza automáticamente
5. **Elimina dirección** → Se marca como inactiva

## 🚨 Casos de Error

### **Límite Excedido**
```json
{
    "error": "Los usuarios consumer pueden tener máximo 3 direcciones."
}
```

### **Sin Permisos**
```json
{
    "error": "No tienes permisos para gestionar esta dirección."
}
```

### **Coordenadas Inválidas**
```json
{
    "error": "La latitud debe estar dentro del rango de Ecuador (-5.0 a 1.5 grados)."
}
```

### **País No Permitido**
```json
{
    "error": "Solo se permiten direcciones de Ecuador."
}
```

## 📈 Próximas Mejoras

- [ ] Integración con Google Places API
- [ ] Cálculo de distancias entre direcciones
- [ ] Geocodificación inversa
- [ ] Validación de códigos postales
- [ ] Historial de direcciones
- [ ] Exportación de direcciones 