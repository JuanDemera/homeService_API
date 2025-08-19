# 💳 API de Pagos - HomeService

## 📋 Descripción

La API de pagos permite simular transacciones de pago para servicios en la plataforma HomeService, incluyendo cálculo de comisiones, validaciones, estadísticas y **referencia a appointments existentes**.

## 🚀 Endpoints

### **Base URL:** `http://tu-servidor:8000/api/payments/`

---

## **1. 🎯 Simular Pago con Referencia a Appointment**

### **Endpoint:**
```http
POST /api/payments/simulate/
```

### **Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

### **Body:**
```json
{
    "cart_id": 1,
    "payment_method": "credit_card",
    "currency": "USD",
    "appointment_id": 123
}
```

### **Campos Requeridos:**
- `cart_id` - ID del carrito (número entero)
- `payment_method` - Método de pago (string)

### **Campos Opcionales:**
- `currency` - Moneda (por defecto "USD")
- `appointment_id` - ID del appointment existente (opcional)

### **Métodos de Pago Disponibles:**
- `credit_card` - Tarjeta de Crédito (3.5% comisión)
- `debit_card` - Tarjeta de Débito (2.5% comisión)
- `cash` - Efectivo (2.0% comisión)
- `transfer` - Transferencia Bancaria (1.5% comisión)
- `paypal` - PayPal (2.9% comisión)



### **Respuesta Exitosa:**
```json
{
    "status": "simulation_success",
    "transaction_id": "sim_a1b2c3d4_1705584000",
    "amount": "155.25",
    "currency": "USD",
    "payment_method": "credit_card",
    "cart_total": "150.00",
    "service_fee": "5.25",
    "total_amount": "155.25",
    "estimated_processing_time": "2-3 segundos",
    "success_probability": 0.95,
    "message": "Transacción simulada exitosamente. Verifique los datos de su tarjeta.",
    "appointment_id": 123
}
```

### **Respuesta de Error:**
```json
{
    "error": "El carrito especificado no existe"
}
```

---

## **2. 📊 Historial de Pagos**

### **Endpoint:**
```http
GET /api/payments/history/
```

### **Headers:**
```
Authorization: Bearer <token>
```

### **Respuesta:**
```json
{
    "payments": [
        {
            "id": 1,
            "amount": "155.25",
            "transaction_type": "payout",
            "description": "Pago por servicios de limpieza",
            "is_completed": true,
            "created_at": "2025-01-18T10:00:00Z",
            "completed_at": "2025-01-18T10:05:00Z"
        }
    ],
    "statistics": {
        "total_payments": 5,
        "completed_payments": 4,
        "pending_payments": 1,
        "total_amount": "620.00",
        "success_rate": 80.0
    }
}
```

---

## **3. 📋 Lista de Pagos**

### **Endpoint:**
```http
GET /api/payments/list/
```

### **Headers:**
```
Authorization: Bearer <token>
```

### **Respuesta:**
```json
[
    {
        "id": 1,
        "amount": "155.25",
        "transaction_type": "payout",
        "description": "Pago por servicios",
        "is_completed": true,
        "created_at": "2025-01-18T10:00:00Z",
        "completed_at": "2025-01-18T10:05:00Z"
    }
]
```

---

## 🧪 **Ejemplos de Prueba**

### **1. Simular Pago con Referencia a Appointment**
```bash
curl -X POST http://localhost:8000/api/payments/simulate/ \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cart_id": 1,
    "payment_method": "credit_card",
    "currency": "USD",
    "appointment_id": 123
  }'
```

### **2. Simular Pago sin Appointment**
```bash
curl -X POST http://localhost:8000/api/payments/simulate/ \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cart_id": 1,
    "payment_method": "cash",
    "currency": "USD"
  }'
```
```

### **3. Obtener Historial**
```bash
curl -X GET http://localhost:8000/api/payments/history/ \
  -H "Authorization: Bearer TU_TOKEN"
```

---

## 📊 **Cálculo de Comisiones**

| Método de Pago | Comisión | Tiempo de Procesamiento | Probabilidad de Éxito |
|----------------|----------|-------------------------|----------------------|
| Tarjeta de Crédito | 3.5% | 2-3 segundos | 95% |
| Tarjeta de Débito | 2.5% | 1-2 segundos | 98% |
| Efectivo | 2.0% | Inmediato | 100% |
| Transferencia | 1.5% | 1-3 días hábiles | 92% |
| PayPal | 2.9% | 30-60 segundos | 97% |

---

## 🔧 **Funcionalidades**

### ✅ **Implementado:**
- ✅ Simulación realista de pagos
- ✅ Cálculo automático de comisiones
- ✅ Validación de carritos
- ✅ Generación de IDs únicos
- ✅ Estadísticas de pagos
- ✅ Manejo de errores
- ✅ Diferentes métodos de pago
- ✅ **Referencia a appointments existentes**
- ✅ **Limpieza automática del carrito**

### 🔄 **Próximas Mejoras:**
- 🔄 Integración con pasarelas reales
- 🔄 Notificaciones de pago
- 🔄 Reembolsos
- 🔄 Facturación electrónica
- 🔄 Reportes avanzados

---

## ⚠️ **Validaciones**

- **Autenticación**: Token JWT requerido
- **Carrito**: Debe existir y pertenecer al usuario
- **Método de Pago**: Debe ser uno de los permitidos
- **Moneda**: Solo USD y EUR soportadas
- **Monto**: Mínimo $0.01
- **Appointment**: Si se proporciona, debe existir y pertenecer al usuario

---

## 🚨 **Códigos de Error**

| Código | Descripción |
|--------|-------------|
| 400 | Datos de entrada inválidos |
| 401 | No autenticado |
| 403 | No tienes permisos para acceder a este carrito/appointment |
| 404 | Carrito o appointment no encontrado |
| 500 | Error interno del servidor |

---

## 📱 **Uso en Flutter**

```dart
// Simular pago con referencia a appointment
Future<Map<String, dynamic>> simulatePayment({
  required int cartId,
  required String paymentMethod,
  String currency = 'USD',
  int? appointmentId,
}) async {
  final response = await http.post(
    Uri.parse('${ApiConfig.baseUrl}/api/payments/simulate/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'cart_id': cartId,
      'payment_method': paymentMethod,
      'currency': currency,
      if (appointmentId != null) 'appointment_id': appointmentId,
    }),
  );
  
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Error en simulación de pago');
  }
}

// Uso:
await simulatePayment(
  cartId: 1,
  paymentMethod: 'credit_card',
  appointmentId: 123  // Opcional
);
```

---

## 🔄 **Flujo Completo**

1. **Usuario selecciona servicios** → Se agregan al carrito
2. **Usuario crea appointment** → Desde Flutter (fecha/hora)
3. **Usuario procede al pago** → Incluye referencia al appointment
4. **Sistema valida datos** → Carrito, appointment, permisos
5. **Sistema procesa pago** → Simulación con comisiones
6. **Sistema limpia carrito** → Items eliminados
7. **Sistema retorna respuesta** → Confirmación con referencia

---

## 📋 **Campos del Request**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `cart_id` | Integer | ✅ | ID del carrito |
| `payment_method` | String | ✅ | Método de pago |
| `currency` | String | ❌ | Moneda (default: USD) |
| `appointment_id` | Integer | ❌ | ID del appointment existente | 