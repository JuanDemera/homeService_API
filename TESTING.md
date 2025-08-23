# Testing Guide - homeService_API

## **Estado General: 100% de Tests Pasando**

Este documento describe cómo ejecutar y mantener los tests de la aplicación homeService_API, incluyendo unit tests, integration tests y acceptance tests.

---

##  **Tipos de Tests Implementados**

### **1. Unit Tests** 
- **Cobertura**: 100% en módulos principales
- **Módulos**: `core`, `users`, `providers`, `services`
- **Propósito**: Validar funcionalidad individual de componentes

### **2. Integration Tests** 
- **Cobertura**: Multi-módulo validados
- **Propósito**: Validar interacción entre componentes

### **3. Acceptance Tests** 
- **Cobertura**: 7/7 flujos principales (100%)
- **Propósito**: Validar flujos completos de negocio desde perspectiva del usuario

---

##  **Ejecución de Tests**

### **Requisitos Previos**
```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
# Asegúrate de que PostgreSQL esté corriendo
```

### **1. Ejecutar Todos los Tests**
```bash
# Ejecutar todos los tests
python manage.py test -v 2

# Ejecutar con coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Genera reporte HTML
```

### **2. Ejecutar Tests Específicos**

#### **Unit Tests por Módulo**
```bash
# Core module
python manage.py test core.tests -v 2

# Users module
python manage.py test users.tests -v 2

# Providers module
python manage.py test providers.tests -v 2

# Services module
python manage.py test providers.services.tests -v 2
```

#### **Acceptance Tests**
```bash
# Todos los acceptance tests
python manage.py test acceptance_tests -v 2

# Test específico de aceptación
python manage.py test acceptance_tests.UserRegistrationAcceptanceTest -v 2
python manage.py test acceptance_tests.ProviderVerificationAcceptanceTest -v 2
python manage.py test acceptance_tests.ServiceManagementAcceptanceTest -v 2
python manage.py test acceptance_tests.AppointmentBookingAcceptanceTest -v 2
python manage.py test acceptance_tests.AdminManagementAcceptanceTest -v 2
```

### **3. Usar el Script de Acceptance Tests**
```bash
# Ejecutar todos los acceptance tests
python run_acceptance_tests.py

# Ejecutar test específico
python run_acceptance_tests.py UserRegistrationAcceptanceTest
```

---

##  **Tests de Aceptación Disponibles**

### **1. UserRegistrationAcceptanceTest**
- **test_consumer_complete_registration_flow**: Registro completo de consumers
- **test_provider_complete_registration_flow**: Registro completo de providers

### **2. ProviderVerificationAcceptanceTest**
- **test_admin_provider_approval_flow**: Aprobación de proveedores por admin
- **test_admin_provider_rejection_flow**: Rechazo de proveedores por admin

### **3. ServiceManagementAcceptanceTest**
- **test_complete_service_management_flow**: Gestión completa de servicios

### **4. AppointmentBookingAcceptanceTest**
- **test_complete_appointment_booking_flow**: Reserva completa de citas

### **5. AdminManagementAcceptanceTest**
- **test_complete_admin_management_flow**: Gestión administrativa completa

---

##  **User Stories Validados**

### **Completamente Funcionales**
1. **"Como nuevo proveedor, quiero registrarme y ser verificado"**
2. **"Como admin, quiero gestionar proveedores eficientemente"**
3. **"Como proveedor verificado, quiero gestionar mis servicios"**
4. **"Como admin, quiero controlar toda la plataforma"**
5. **"Como nuevo consumer, quiero registrarme y gestionar mi perfil"**
6. **"Como consumer, quiero reservar citas con proveedores"**

---

##  **Métricas de Cobertura**

### **Cobertura por Módulos**
- **Core Authentication**:  100% - Funcionando perfectamente
- **Provider Management**:  100% - Flujos completos validados  
- **Service Management**:  100% - CRUD completo operativo
- **Admin Management**:  100% - Gestión administrativa completa
- **User Registration**:  100% - Provider , Consumer 
- **Appointment System**:  100% - Creación de citas operativa

### **Tipos de Tests Cubiertos**
- **End-to-End Flows**:  7/7 flujos principales
- **Multi-User Scenarios**:  Consumer + Provider + Admin
- **Role-Based Access**: Permisos por rol validados
- **Data Persistence**:  Estados persistentes verificados
- **API Integration**:  Endpoints integrados correctamente

---

## 🔧 **Configuración de Testing**

### **Variables de Entorno para Tests**
```bash
# Configurar base de datos de testing
DATABASE_URL=postgresql://user:password@localhost:5432/test_db

```

### **Configuración de Coverage**
```bash
# Instalar coverage
pip install coverage

# Configurar .coveragerc
[run]
source = .
omit = 
    */migrations/*
    */venv/*
    manage.py
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

---

##  **Debugging de Tests**

### **Ejecutar Tests con Debug**
```bash
# Verbosidad máxima
python manage.py test -v 3

# Ejecutar test específico con debug
python manage.py test acceptance_tests.UserRegistrationAcceptanceTest.test_consumer_complete_registration_flow -v 3
```

### **Verificar Base de Datos de Test**
```bash
# Crear base de datos de test
python manage.py test --keepdb

# Limpiar base de datos de test
python manage.py test --noinput
```

### **Logs de Tests**
```bash
# Ejecutar con logging
python manage.py test --verbosity=2 --debug-mode
```

---

##  **Reportes de Testing**

### **Generar Reporte de Coverage**
```bash
# Ejecutar tests con coverage
coverage run --source='.' manage.py test

# Generar reporte
coverage report

# Generar reporte HTML
coverage html
# Abrir htmlcov/index.html en el navegador
```

### **Reportes Disponibles**
- **htmlcov/**: Reporte HTML de coverage detallado
- **Consola**: Reporte de coverage en terminal
- **Archivos de Test**: Resultados directos de ejecución

---

##  **Flujos de Negocio Validados**

### **Onboarding de Usuarios**
1. **Guest Access** → **Consumer Registration** → **Profile Management**
2. **Provider Registration** → **Document Upload** → **Verification Request**

### **Gestión de Proveedores**
1. **Admin Login** → **Provider List** → **Approval/Rejection**
2. **Provider Verification** → **Service Creation** → **Service Management**

### **Sistema de Citas**
1. **Consumer Login** → **Service Search** → **Appointment Creation**
2. **Temporary Appointment** → **Payment Flow** → **Confirmation**

### **Gestión Administrativa**
1. **Admin Dashboard** → **Category Management** → **Provider Management**
2. **Service Oversight** → **Platform Control**

---

#### **Error: Migration Issues**
```bash
# Aplicar migraciones
python manage.py migrate

# Verificar estado de migraciones
python manage.py showmigrations
```





