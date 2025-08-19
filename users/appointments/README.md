# 📅 API de Appointments - HomeService

## 📋 Descripción

La API de appointments permite gestionar citas entre consumidores y proveedores de servicios, incluyendo creación, edición, cancelación y consulta de disponibilidad. **Los providers pueden ver y gestionar todos los appointments relacionados con sus servicios.**

### 🔄 **Sistema de Appointments Temporales**

- **Appointments temporales**: Se crean automáticamente cuando un usuario reserva una cita
- **Expiración automática**: Los appointments temporales expiran después de 30 minutos si no se completa el pago
- **Limpieza automática**: Los appointments expirados se eliminan automáticamente del sistema
- **Confirmación por pago**: Solo los appointments pagados se convierten en citas confirmadas

## 🚀 Endpoints

### **Base URL:** `http://tu-servidor:8000/api/appointments/`

---

## **1. 👤 Endpoints para Consumidores**

### **1.1 📋 Listar Appointments del Consumidor**

#### **Endpoint:**
```http
GET /api/appointments/consumer/
```

#### **Headers:**
```
Authorization: Bearer <token>
```

#### **Parámetros de Filtro (Opcionales):**
- `status` - Filtrar por estado (pending, confirmed, completed, cancelled, temporary)
- `date` - Filtrar por fecha específica (YYYY-MM-DD)
- `include_temporary` - Incluir appointments temporales (true/false, default: false)

#### **Ejemplo:**
```http
GET /api/appointments/consumer/?status=pending&date=2025-01-25&include_temporary=true
```

#### **Respuesta:**
```json
[
    {
        "id": 1,
        "consumer": {
            "id": 1,
            "username": "usuario1",
            "email": "usuario1@example.com"
        },
        "provider": {
            "id": 2,
            "username": "proveedor1",
            "email": "proveedor1@example.com"
        },
        "service": {
            "id": 1,
            "title": "Limpieza de Casa",
            "description": "Servicio de limpieza completa",
            "price": "50.00"
        },
        "appointment_date": "2025-01-25",
        "appointment_time": "14:30:00",
        "status": "temporary",
        "notes": "Por favor llegar 10 minutos antes",
        "created_at": "2025-01-18T10:00:00Z",
        "updated_at": "2025-01-18T10:00:00Z",
        "is_temporary": true,
        "expires_at": "2025-01-18T10:30:00Z",
        "payment_completed": false,
        "payment_reference": null,
        "is_expired": false,
        "time_until_expiry": "00:25:30"
    }
]
```

---

### **1.2 ➕ Crear Nuevo Appointment (Temporal)**

#### **Endpoint:**
```http
POST /api/appointments/consumer/create/
```

#### **Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

#### **Body:**
```json
{
    "service": 1,
    "appointment_date": "2025-01-25",
    "appointment_time": "14:30",
    "notes": "Por favor llegar 10 minutos antes",
    "service_address": "Av. Amazonas 123, Quito, Ecuador",
    "service_latitude": -0.2298500,
    "service_longitude": -78.5249500
}
```

#### **Campos Requeridos:**
- `service` - ID del servicio (número entero)
- `appointment_date` - Fecha de la cita (YYYY-MM-DD)
- `appointment_time` - Hora de la cita (HH:MM)

#### **Campos Opcionales:**
- `notes` - Notas adicionales (string)
- `service_address` - Dirección donde se prestará el servicio (string)
- `service_latitude` - Latitud de la dirección (decimal)
- `service_longitude` - Longitud de la dirección (decimal)

#### **Validaciones:**
- La fecha no puede ser en el pasado
- La fecha no puede ser más de 3 meses en el futuro
- Las citas deben estar entre las 6:00 AM y 10:00 PM
- No se permiten citas los domingos

#### **Respuesta Exitosa:**
```json
{
    "id": 1,
    "consumer": 1,
    "provider": 2,
    "service": 1,
    "appointment_date": "2025-01-25",
    "appointment_time": "14:30:00",
    "status": "temporary",
    "notes": "Por favor llegar 10 minutos antes",
    "service_address": "Av. Amazonas 123, Quito, Ecuador",
    "service_latitude": "-0.229850",
    "service_longitude": "-78.524950",
    "created_at": "2025-01-18T10:00:00Z",
    "updated_at": "2025-01-18T10:00:00Z",
    "is_temporary": true,
    "expires_at": "2025-01-18T10:30:00Z",
    "time_until_expiry": "00:30:00",
    "message": "Appointment creado temporalmente. Complete el pago para confirmarlo."
}
```

---

### **1.3 👁️ Ver Detalles de Appointment**

#### **Endpoint:**
```http
GET /api/appointments/consumer/{appointment_id}/
```

#### **Headers:**
```
Authorization: Bearer <token>
```

#### **Respuesta:**
```json
{
    "id": 1,
    "consumer": {
        "id": 1,
        "username": "usuario1",
        "email": "usuario1@example.com"
    },
    "provider": {
        "id": 2,
        "username": "proveedor1",
        "email": "proveedor1@example.com"
    },
    "service": {
        "id": 1,
        "title": "Limpieza de Casa",
        "description": "Servicio de limpieza completa",
        "price": "50.00"
    },
    "appointment_date": "2025-01-25",
    "appointment_time": "14:30:00",
    "status": "temporary",
    "notes": "Por favor llegar 10 minutos antes",
    "created_at": "2025-01-18T10:00:00Z",
    "updated_at": "2025-01-18T10:00:00Z",
    "is_temporary": true,
    "expires_at": "2025-01-18T10:30:00Z",
    "payment_completed": false,
    "payment_reference": null,
    "is_expired": false,
    "time_until_expiry": "00:25:30"
}
```

---

### **1.4 ✏️ Editar Appointment**

#### **Endpoint:**
```http
PUT /api/appointments/consumer/{appointment_id}/update/
```

#### **Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

#### **Body:**
```json
{
    "appointment_date": "2025-01-26",
    "appointment_time": "15:00",
    "notes": "Cambio de horario solicitado"
}
```

#### **Campos Opcionales:**
- `appointment_date` - Nueva fecha (YYYY-MM-DD)
- `appointment_time` - Nueva hora (HH:MM)
- `notes` - Nuevas notas

#### **Validaciones:**
- No se puede editar un appointment temporal expirado
- Las mismas validaciones de fecha y hora que en la creación

#### **Respuesta:**
```json
{
    "message": "Appointment actualizado correctamente",
    "appointment": {
        "id": 1,
        "appointment_date": "2025-01-26",
        "appointment_time": "15:00:00",
        "notes": "Cambio de horario solicitado",
        "status": "temporary"
    }
}
```

---

### **1.5 ❌ Cancelar Appointment**

#### **Endpoint:**
```http
PUT /api/appointments/consumer/{appointment_id}/cancel/
```

#### **Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

#### **Body:**
```json
{
    "notes": "Cancelación por emergencia familiar"
}
```

#### **Respuesta:**
```json
{
    "message": "Cita cancelada correctamente",
    "status": "cancelled"
}
```

---

### **1.6 💳 Marcar Appointment como Pagado**

#### **Endpoint:**
```http
PUT /api/appointments/consumer/{appointment_id}/mark-paid/
```

#### **Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

#### **Body:**
```json
{
    "payment_reference": "TXN_123456789"
}
```

#### **Campos Opcionales:**
- `payment_reference` - Referencia del pago (string)

#### **Validaciones:**
- Solo se pueden marcar appointments temporales
- No se puede marcar un appointment expirado
- No se puede marcar un appointment ya pagado

#### **Respuesta:**
```json
{
    "message": "Appointment marcado como pagado correctamente",
    "appointment": {
        "id": 1,
        "status": "pending",
        "is_temporary": false,
        "payment_completed": true,
        "payment_reference": "TXN_123456789"
    }
}
```

---

## **2. 🏢 Endpoints para Proveedores**

### **2.1 📋 Listar Appointments del Proveedor**

#### **Endpoint:**
```http
GET /api/appointments/provider/
```

#### **Headers:**
```
Authorization: Bearer <token>
```

#### **Parámetros de Filtro (Opcionales):**
- `status` - Filtrar por estado (pending, confirmed, completed, cancelled)
- `date` - Filtrar por fecha específica (YYYY-MM-DD)
- `service_id` - Filtrar por servicio específico
- `date_range` - Filtrar por rango de fechas (today, week, month)

#### **Ejemplos:**
```http
# Todos los appointments (excluye temporales no pagados)
GET /api/appointments/provider/

# Solo appointments pendientes
GET /api/appointments/provider/?status=pending

# Appointments de hoy
GET /api/appointments/provider/?date_range=today

# Appointments de un servicio específico
GET /api/appointments/provider/?service_id=1

# Appointments de esta semana
GET /api/appointments/provider/?date_range=week
```

#### **Respuesta:** Similar a consumer pero filtrado por provider (excluye temporales no pagados)

---

### **2.2 👁️ Ver Detalles de Appointment (Provider)**

#### **Endpoint:**
```http
GET /api/appointments/provider/{appointment_id}/
```

#### **Headers:**
```
Authorization: Bearer <token>
```

---

### **2.3 ✏️ Actualizar Estado de Appointment**

#### **Endpoint:**
```http
PUT /api/appointments/provider/{appointment_id}/update/
```

#### **Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

#### **Body:**
```json
{
    "status": "confirmed",
    "notes": "Cita confirmada, llegaremos a tiempo"
}
```

#### **Estados Permitidos:**
- `pending` → `confirmed`, `cancelled`
- `confirmed` → `completed`, `cancelled`
- `completed` → (no se puede cambiar)
- `cancelled` → (no se puede cambiar)

#### **Respuesta:**
```json
{
    "message": "Estado de la cita actualizado correctamente",
    "status": "confirmed"
}
```

---

### **2.4 📊 Dashboard del Provider**

#### **Endpoint:**
```http
GET /api/appointments/provider/dashboard/
```

#### **Headers:**
```
Authorization: Bearer <token>
```

#### **Respuesta:**
```json
{
    "service_statistics": [
        {
            "service_id": 1,
            "service_title": "Limpieza de Casa",
            "total_appointments": 15,
            "pending": 3,
            "confirmed": 8,
            "completed": 3,
            "cancelled": 1
        }
    ],
    "today_appointments": [
        {
            "id": 1,
            "appointment_date": "2025-01-18",
            "appointment_time": "14:30:00",
            "status": "confirmed",
            "consumer": {
                "id": 1,
                "username": "usuario1"
            },
            "service": {
                "id": 1,
                "title": "Limpieza de Casa"
            }
        }
    ],
    "tomorrow_appointments": [...],
    "total_appointments": 25,
    "pending_appointments": 5,
    "confirmed_appointments": 12
}
```

---

### **2.5 🔍 Appointments por Servicio**

#### **Endpoint:**
```http
GET /api/appointments/provider/service/{service_id}/
```

#### **Headers:**
```
Authorization: Bearer <token>
```

#### **Parámetros de Filtro (Opcionales):**
- `status` - Filtrar por estado
- `date` - Filtrar por fecha específica

#### **Ejemplo:**
```http
GET /api/appointments/provider/service/1/?status=pending
```

---

## **3. 📊 Endpoints Generales**

### **3.1 📈 Estadísticas de Appointments**

#### **Endpoint:**
```http
GET /api/appointments/statistics/
```

#### **Headers:**
```
Authorization: Bearer <token>
```

#### **Respuesta para Consumidor:**
```json
{
    "total": 10,
    "pending": 3,
    "confirmed": 4,
    "completed": 2,
    "cancelled": 1
}
```

#### **Respuesta para Provider:**
```json
{
    "total": 25,
    "pending": 5,
    "confirmed": 12,
    "completed": 6,
    "cancelled": 2,
    "today_appointments": 3,
    "upcoming_appointments": 8
}
```

---

### **3.2 🔍 Verificar Disponibilidad**

#### **Endpoint:**
```http
GET /api/appointments/availability/?service_id=1&date=2025-01-25
```

#### **Headers:**
```
Authorization: Bearer <token>
```

#### **Parámetros:**
- `service_id` - ID del servicio (requerido)
- `date` - Fecha a verificar (YYYY-MM-DD, requerido)

#### **Respuesta:**
```json
{
    "service_id": 1,
    "date": "2025-01-25",
    "available_times": ["09:00", "10:00", "11:00", "15:00", "16:00"],
    "occupied_times": ["14:00", "17:00"]
}
```

---

## 🧪 **Ejemplos de Prueba**

### **1. Crear Appointment Temporal**
```bash
curl -X POST http://localhost:8000/api/appointments/consumer/create/ \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service": 1,
    "appointment_date": "2025-01-25",
    "appointment_time": "14:30",
    "notes": "Por favor llegar 10 minutos antes"
  }'
```

### **2. Marcar como Pagado**
```bash
curl -X PUT http://localhost:8000/api/appointments/consumer/1/mark-paid/ \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_reference": "TXN_123456789"
  }'
```

### **3. Editar Appointment**
```bash
curl -X PUT http://localhost:8000/api/appointments/consumer/1/update/ \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "appointment_time": "15:00",
    "notes": "Cambio de horario"
  }'
```

### **4. Cancelar Appointment**
```bash
curl -X PUT http://localhost:8000/api/appointments/consumer/1/cancel/ \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Cancelación por emergencia"
  }'
```

### **5. Verificar Disponibilidad**
```bash
curl -X GET "http://localhost:8000/api/appointments/availability/?service_id=1&date=2025-01-25" \
  -H "Authorization: Bearer TU_TOKEN"
```

### **6. Dashboard del Provider**
```bash
curl -X GET http://localhost:8000/api/appointments/provider/dashboard/ \
  -H "Authorization: Bearer TU_TOKEN"
```

### **7. Appointments por Servicio**
```bash
curl -X GET "http://localhost:8000/api/appointments/provider/service/1/?status=pending" \
  -H "Authorization: Bearer TU_TOKEN"
```

---

## 📱 **Uso en Flutter**

```dart
// Crear appointment temporal
Future<Map<String, dynamic>> createAppointment({
  required int serviceId,
  required DateTime appointmentDate,
  required TimeOfDay appointmentTime,
  String? notes,
}) async {
  final response = await http.post(
    Uri.parse('${ApiConfig.baseUrl}/api/appointments/consumer/create/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'service': serviceId,
      'appointment_date': '${appointmentDate.year}-${appointmentDate.month.toString().padLeft(2, '0')}-${appointmentDate.day.toString().padLeft(2, '0')}',
      'appointment_time': '${appointmentTime.hour.toString().padLeft(2, '0')}:${appointmentTime.minute.toString().padLeft(2, '0')}',
      if (notes != null) 'notes': notes,
    }),
  );
  
  if (response.statusCode == 201) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Error creando appointment');
  }
}

// Marcar como pagado
Future<Map<String, dynamic>> markAppointmentAsPaid({
  required int appointmentId,
  String? paymentReference,
}) async {
  final response = await http.put(
    Uri.parse('${ApiConfig.baseUrl}/api/appointments/consumer/$appointmentId/mark-paid/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      if (paymentReference != null) 'payment_reference': paymentReference,
    }),
  );
  
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Error marcando appointment como pagado');
  }
}

// Editar appointment
Future<Map<String, dynamic>> updateAppointment({
  required int appointmentId,
  DateTime? appointmentDate,
  TimeOfDay? appointmentTime,
  String? notes,
}) async {
  final Map<String, dynamic> data = {};
  
  if (appointmentDate != null) {
    data['appointment_date'] = '${appointmentDate.year}-${appointmentDate.month.toString().padLeft(2, '0')}-${appointmentDate.day.toString().padLeft(2, '0')}';
  }
  
  if (appointmentTime != null) {
    data['appointment_time'] = '${appointmentTime.hour.toString().padLeft(2, '0')}:${appointmentTime.minute.toString().padLeft(2, '0')}';
  }
  
  if (notes != null) {
    data['notes'] = notes;
  }
  
  final response = await http.put(
    Uri.parse('${ApiConfig.baseUrl}/api/appointments/consumer/$appointmentId/update/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode(data),
  );
  
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Error actualizando appointment');
  }
}

// Verificar disponibilidad
Future<Map<String, dynamic>> checkAvailability({
  required int serviceId,
  required DateTime date,
}) async {
  final response = await http.get(
    Uri.parse('${ApiConfig.baseUrl}/api/appointments/availability/?service_id=$serviceId&date=${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}'),
    headers: {
      'Authorization': 'Bearer $token',
    },
  );
  
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Error verificando disponibilidad');
  }
}

// Dashboard del provider
Future<Map<String, dynamic>> getProviderDashboard() async {
  final response = await http.get(
    Uri.parse('${ApiConfig.baseUrl}/api/appointments/provider/dashboard/'),
    headers: {
      'Authorization': 'Bearer $token',
    },
  );
  
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Error obteniendo dashboard');
  }
}

// Appointments por servicio
Future<List<Map<String, dynamic>>> getServiceAppointments({
  required int serviceId,
  String? status,
  String? date,
}) async {
  final queryParams = <String, String>{};
  if (status != null) queryParams['status'] = status;
  if (date != null) queryParams['date'] = date;
  
  final uri = Uri.parse('${ApiConfig.baseUrl}/api/appointments/provider/service/$serviceId/')
      .replace(queryParameters: queryParams.isNotEmpty ? queryParams : null);
  
  final response = await http.get(
    uri,
    headers: {
      'Authorization': 'Bearer $token',
    },
  );
  
  if (response.statusCode == 200) {
    final List<dynamic> data = jsonDecode(response.body);
    return data.cast<Map<String, dynamic>>();
  } else {
    throw Exception('Error obteniendo appointments del servicio');
  }
}
```

---

## ⚠️ **Validaciones**

- **Autenticación**: Token JWT requerido
- **Permisos**: Solo el propietario puede modificar sus appointments
- **Fechas**: No pueden ser en el pasado ni más de 3 meses en el futuro
- **Horarios**: Entre 6:00 AM y 10:00 PM
- **Días**: No se permiten citas los domingos
- **Estados**: Solo transiciones válidas permitidas
- **Appointments temporales**: Expiran después de 30 minutos si no se pagan

---

## 🚨 **Códigos de Error**

| Código | Descripción |
|--------|-------------|
| 400 | Datos de entrada inválidos |
| 401 | No autenticado |
| 403 | No tienes permisos para modificar este appointment |
| 404 | Appointment no encontrado |
| 500 | Error interno del servidor |

---

## 🔄 **Estados de Appointment**

| Estado | Descripción | Transiciones Permitidas |
|--------|-------------|-------------------------|
| `temporary` | Temporal (no pagado) | `pending` (al pagar) |
| `pending` | Pendiente de confirmación | `confirmed`, `cancelled` |
| `confirmed` | Confirmado por el proveedor | `completed`, `cancelled` |
| `completed` | Servicio completado | Ninguna |
| `cancelled` | Cancelado | Ninguna |

---

## 🧹 **Limpieza Automática**

### **Comando de Limpieza**
```bash
# Ver qué appointments serían eliminados (dry run)
python manage.py cleanup_expired_appointments --dry-run

# Eliminar appointments expirados
python manage.py cleanup_expired_appointments

# Especificar tiempo de expiración personalizado (en minutos)
python manage.py cleanup_expired_appointments --minutes 45
```

### **Configuración de Cron Job (Linux/Mac)**
```bash
# Agregar al crontab para ejecutar cada 15 minutos
*/15 * * * * cd /path/to/your/project && python manage.py cleanup_expired_appointments
```

### **Configuración de Task Scheduler (Windows)**
1. Abrir Task Scheduler
2. Crear tarea básica
3. Programar para ejecutar cada 15 minutos
4. Acción: Iniciar programa
5. Programa: `python`
6. Argumentos: `manage.py cleanup_expired_appointments`
7. Iniciar en: `C:\path\to\your\project`

---

## 📋 **Flujo Completo del Sistema**

### **Para Consumidores:**
1. **Crear appointment** → Se crea como temporal (30 min de expiración)
2. **Completar pago** → Appointment se marca como pagado y cambia a "pending"
3. **Esperar confirmación** → Provider confirma la cita
4. **Servicio completado** → Provider marca como "completed"

### **Para Providers:**
1. **Ver appointments confirmados** → Solo ve appointments pagados
2. **Confirmar appointments** → Cambia estado a "confirmed"
3. **Gestionar citas del día** → Ve citas de hoy y mañana
4. **Completar servicios** → Marca como "completed"

### **Limpieza Automática:**
1. **Appointments temporales** → Se crean con expiración de 30 minutos
2. **Verificación periódica** → Comando se ejecuta cada 15 minutos
3. **Eliminación automática** → Appointments expirados se eliminan
4. **Logs de auditoría** → Se registran las eliminaciones

---

## 🎯 **Funcionalidades Clave**

### **Para Consumidores:**
- ✅ **Creación temporal** de appointments con expiración
- ✅ **Pago y confirmación** automática
- ✅ **Edición** de appointments no expirados
- ✅ **Cancelación** de appointments pendientes
- ✅ **Verificación de disponibilidad** en tiempo real

### **Para Providers:**
- ✅ **Dashboard completo** con estadísticas y próximas citas
- ✅ **Filtros avanzados** por estado, fecha, servicio
- ✅ **Gestión por servicio** - ver appointments de cada servicio
- ✅ **Estadísticas detalladas** por servicio y período
- ✅ **Citas de hoy y mañana** para planificación
- ✅ **Actualización de estados** con validaciones

### **Sistema Automático:**
- ✅ **Expiración automática** de appointments temporales
- ✅ **Limpieza automática** de appointments expirados
- ✅ **Logs de auditoría** para seguimiento
- ✅ **Configuración flexible** de tiempos de expiración 