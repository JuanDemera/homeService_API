# 🏠 HomeService API

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.2+-green.svg)](https://www.djangoproject.com/)
[![Django REST](https://img.shields.io/badge/Django%20REST-3.16+-red.svg)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-20+-blue.svg)](https://www.docker.com/)
[![Coverage](https://img.shields.io/badge/Coverage-85%25+-brightgreen.svg)](TEST_SUMMARY.md)

> **Backend API** para la plataforma HomeService - Conectando consumidores con proveedores de servicios domésticos en Ecuador.

## 📋 Tabla de Contenidos

- [🎯 Descripción](#-descripción)
- [🏗️ Arquitectura](#️-arquitectura)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [🚀 Instalación](#-instalación)
- [🔧 Configuración](#-configuración)
- [🧪 Testing](#-testing)
- [📚 Documentación API](#-documentación-api)
- [🔐 Autenticación](#-autenticación)
- [📊 Endpoints Principales](#-endpoints-principales)
- [🛠️ Tecnologías](#️-tecnologías)
- [📈 Estado del Proyecto](#-estado-del-proyecto)
- [🤝 Contribución](#-contribución)
- [📄 Licencia](#-licencia)

## 🎯 Descripción

HomeService API es una plataforma completa de servicios domésticos que conecta **consumidores** con **proveedores** de servicios en Ecuador. La API proporciona funcionalidades robustas para gestión de usuarios, citas, pagos y servicios.

### ✨ Características Principales

- 🔐 **Autenticación JWT** con roles múltiples
- 📱 **Sistema OTP** para verificación de usuarios (WhatsApp/Email)
- 👥 **Gestión de perfiles** para consumidores y proveedores
- 📅 **Sistema de citas** con estados y pagos
- 💳 **Integración de pagos** (en desarrollo)
- 🖼️ **Almacenamiento de imágenes** seguro
- 📍 **Gestión de direcciones** y geolocalización
- 🛒 **Carritos de compra** para múltiples servicios
- 📊 **Reportes y analytics** para administradores

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   HomeService   │    │   PostgreSQL    │
│   (Flutter)     │◄──►│      API        │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Cache Local   │
                       │   (OTP/Session) │
                       └─────────────────┘
```

## 📁 Estructura del Proyecto

```
homeService_API/
├── 📂 backend_homeService/          # Configuración principal de Django
│   ├── settings.py                  # Configuración del proyecto
│   ├── urls.py                      # URLs principales
│   ├── wsgi.py                      # Configuración WSGI
│   └── asgi.py                      # Configuración ASGI
│
├── 📂 core/                         # Módulo central de autenticación
│   ├── models.py                    # Modelo de usuario personalizado
│   ├── serializers.py               # Serializers de autenticación
│   ├── views.py                     # Vistas de autenticación
│   ├── authentication.py            # Lógica de autenticación
│   ├── backends.py                  # Backends de autenticación
│   ├── managers.py                  # Manager personalizado de usuarios
│   └── tests.py                     # Tests de autenticación
│
├── 📂 users/                        # Gestión de usuarios y perfiles
│   ├── models.py                    # Modelo de perfil de usuario
│   ├── serializers.py               # Serializers de usuarios
│   ├── views.py                     # Vistas de usuarios
│   ├── utils/
│   │   └── otp.py                   # Utilidades para OTP
│   ├── 📂 appointments/             # Sistema de citas
│   │   ├── models.py                # Modelo de citas
│   │   ├── serializers.py           # Serializers de citas
│   │   ├── views.py                 # Vistas de citas
│   │   ├── tests.py                 # Tests de citas
│   │   └── management/
│   │       └── commands/
│   │           └── cleanup_expired_appointments.py
│   └── 📂 carts/                    # Carritos de compra
│       ├── models.py                # Modelo de carrito
│       ├── serializers.py           # Serializers de carrito
│       ├── views.py                 # Vistas de carrito
│       ├── signals.py               # Señales de carrito
│       └── tests.py                 # Tests de carrito
│
├── 📂 providers/                    # Gestión de proveedores
│   ├── models.py                    # Modelo de proveedor
│   ├── serializers.py               # Serializers de proveedores
│   ├── views.py                     # Vistas de proveedores
│   ├── signals.py                   # Señales de proveedores
│   ├── tests.py                     # Tests de proveedores
│   ├── 📂 services/                 # Servicios ofrecidos
│   │   ├── models.py                # Modelo de servicios
│   │   ├── serializers.py           # Serializers de servicios
│   │   ├── views.py                 # Vistas de servicios
│   │   └── tests.py                 # Tests de servicios
│   ├── 📂 payments/                 # Sistema de pagos
│   │   ├── models.py                # Modelo de pagos
│   │   ├── serializers.py           # Serializers de pagos
│   │   ├── views.py                 # Vistas de pagos
│   │   ├── services.py              # Servicios de pago
│   │   └── tests.py                 # Tests de pagos
│   └── 📂 fee_policies/             # Políticas de comisiones
│       ├── models.py                # Modelo de políticas
│       ├── serializers.py           # Serializers de políticas
│       ├── views.py                 # Vistas de políticas
│       └── tests.py                 # Tests de políticas
│
├── 📂 addresses/                    # Gestión de direcciones
│   ├── models.py                    # Modelo de direcciones
│   ├── serializers.py               # Serializers de direcciones
│   ├── views.py                     # Vistas de direcciones
│   ├── permissions.py               # Permisos de direcciones
│   └── tests.py                     # Tests de direcciones
│
├── 📂 image_storage/                # Almacenamiento de imágenes
│   ├── models.py                    # Modelo de imágenes
│   ├── serializers.py               # Serializers de imágenes
│   ├── views.py                     # Vistas de imágenes
│   ├── services.py                  # Servicios de imágenes
│   ├── signals.py                   # Señales de imágenes
│   ├── permissions.py               # Permisos de imágenes
│   └── tests.py                     # Tests de imágenes
│
├── 📂 media/                        # Archivos multimedia subidos
├── 📂 static/                       # Archivos estáticos
├── 📂 venv/                         # Entorno virtual (ignorado)
│
├── 📄 requirements.txt              # Dependencias de Python
├── 📄 win_requirements.txt          # Dependencias para Windows
├── 📄 docker-compose.yaml           # Configuración de Docker
├── 📄 manage.py                     # Script de gestión de Django
├── 📄 .coveragerc                   # Configuración de coverage
├── 📄 run_tests.py                  # Script de ejecución de tests
├── 📄 install_test_deps.py          # Instalación de dependencias de testing
├── 📄 TESTING.md                    # Guía completa de testing
├── 📄 TEST_SUMMARY.md               # Resumen de tests implementados
└── 📄 README.md                     # Este archivo
```

## 🚀 Instalación

### Prerrequisitos

- **Python 3.8+**
- **PostgreSQL 13+**
- **Docker & Docker Compose** (opcional)
- **Git**

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/homeService_API.git
cd homeService_API
```

### 2. Configurar base de datos

**Opción A: Con Docker (Recomendado)**

```bash
# Levantar PostgreSQL con Docker
docker-compose up -d

# Verificar que está funcionando
docker-compose ps
```

**Opción B: PostgreSQL local**

```bash
# Crear base de datos
createdb HS_DB
createdb hs_user
```

### 3. Configurar entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
# Instalar dependencias principales
pip install -r requirements.txt

# Instalar dependencias de testing
python install_test_deps.py
```

### 5. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Django
SECRET_KEY=tu-clave-secreta-aqui
DJANGO_ENV=development
DEBUG=True

# Base de datos
DB_NAME=HS_DB
DB_USER=hs_user
DB_PASSWORD=hs_password
DB_HOST=localhost
DB_PORT=5432

# Cache local (para OTP y sesiones)
# REDIS_URL=redis://localhost:6379/0  # Opcional para futuro

# Configuración de correo (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password
```

### 6. Aplicar migraciones

**⚠️ IMPORTANTE**: Es crucial seguir este orden específico para evitar errores de migración:

```bash
# 1. Migrar core PRIMERO (modelo de usuario personalizado)
python manage.py makemigrations core
python manage.py migrate core

# 2. Migrar users (depende de core)
python manage.py makemigrations users
python manage.py migrate users

# 3. Migrar providers (depende de core y users)
python manage.py makemigrations providers
python manage.py migrate providers

# 4. Migrar addresses
python manage.py makemigrations addresses
python manage.py migrate addresses

# 5. Migrar image_storage
python manage.py makemigrations image_storage
python manage.py migrate image_storage

# 6. Migrar sub-apps de providers
python manage.py makemigrations providers.services
python manage.py migrate providers.services
python manage.py makemigrations providers.payments
python manage.py migrate providers.payments
python manage.py makemigrations providers.fee_policies
python manage.py migrate providers.fee_policies

# 7. Migrar sub-apps de users
python manage.py makemigrations users.appointments
python manage.py migrate users.appointments
python manage.py makemigrations users.carts
python manage.py migrate users.carts

# 8. Finalmente, aplicar cualquier migración restante
python manage.py makemigrations
python manage.py migrate
```

**💡 Nota**: Este orden es importante porque:
- `core` define el modelo de usuario personalizado
- `users` y `providers` dependen del modelo de usuario
- Las sub-apps dependen de sus apps padre
- Las migraciones se aplican en cascada

### 7. Crear superusuario

```bash
python manage.py createsuperuser
```

### 8. Ejecutar el servidor

```bash
# Ejecutar en modo desarrollo
python manage.py runserver

# O ejecutar en un puerto específico
python manage.py runserver 0.0.0.0:8000

# Para producción (con Gunicorn)
gunicorn backend_homeService.wsgi:application --bind 0.0.0.0:8000
```

🎉 **¡Listo!** Tu API está funcionando en: http://127.0.0.1:8000/

### 9. Verificar la instalación

```bash
# Verificar que el servidor responde
curl http://127.0.0.1:8000/api/test-connection/

# Verificar documentación Swagger
# Abrir en navegador: http://127.0.0.1:8000/swagger/
```

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clave secreta de Django | Requerida |
| `DJANGO_ENV` | Entorno (development/production) | development |
| `DEBUG` | Modo debug | True |
| `DB_NAME` | Nombre de la base de datos | HS_DB |
| `DB_USER` | Usuario de la base de datos | hs_user |
| `DB_PASSWORD` | Contraseña de la base de datos | hs_password |
| `DB_HOST` | Host de la base de datos | localhost |
| `DB_PORT` | Puerto de la base de datos | 5432 |

### Configuración de Base de Datos

La API utiliza PostgreSQL como base de datos principal. La configuración se encuentra en `backend_homeService/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'HS_DB',
        'USER': 'hs_user',
        'PASSWORD': 'hs_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Ejecutar todos los tests con coverage
python run_tests.py --coverage --html

# Ejecutar tests de un módulo específico
python run_tests.py --app core --coverage

# Ejecutar tests en modo verbose
python run_tests.py --verbose

# Ejecutar tests en paralelo
python run_tests.py --parallel
```

### Cobertura de Código

- **Cobertura Total**: 85%+
- **Tests Implementados**: 115+ tests
- **Módulos Cubiertos**: Core, Users, Providers, Appointments, Services

📊 **Ver reporte de coverage**: `coverage_html/index.html`

📚 **Documentación de testing**: [TESTING.md](TESTING.md)

## 📚 Documentación API

### Swagger UI

Accede a la documentación interactiva de la API:

**URL**: http://127.0.0.1:8000/swagger/

### Endpoints Principales

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|---------------|
| `/api/token/` | POST | Obtener tokens JWT | No |
| `/api/token/refresh/` | POST | Renovar token | Sí |
| `/api/users/guest-access/` | POST | Crear usuario guest | No |
| `/api/users/send-otp/` | POST | Enviar código OTP | No |
| `/api/users/verify-otp/` | POST | Verificar código OTP | No |
| `/api/users/register-consumer/` | POST | Registrar consumidor | No |
| `/api/users/consumer-profile/` | GET/PUT | Perfil de consumidor | Sí |
| `/api/providers/register/` | POST | Registrar proveedor | No |
| `/api/providers/verification-request/` | PUT | Solicitar verificación | Sí |
| `/api/appointments/create/` | POST | Crear cita | Sí |
| `/api/appointments/consumer/` | GET | Citas del consumidor | Sí |
| `/api/appointments/provider/` | GET | Citas del proveedor | Sí |

## 🔐 Autenticación

### JWT Tokens

La API utiliza JWT (JSON Web Tokens) para autenticación:

```bash
# Obtener token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario", "password": "contraseña"}'

# Usar token
curl -X GET http://127.0.0.1:8000/api/users/consumer-profile/ \
  -H "Authorization: Bearer <tu-token>"
```

### Roles de Usuario

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| `GUEST` | Usuario temporal | Acceso limitado |
| `CONSUMER` | Consumidor de servicios | Crear citas, gestionar perfil |
| `PROVIDER` | Proveedor de servicios | Crear servicios, gestionar citas |
| `MANAGEMENT` | Administrador | Acceso completo |

### Sistema OTP

Para verificación de usuarios:

```bash
# Enviar OTP
curl -X POST http://127.0.0.1:8000/api/users/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+593991234567"}'

# Verificar OTP
curl -X POST http://127.0.0.1:8000/api/users/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+593991234567", "otp": "123456"}'
```

## 📊 Endpoints Principales

### 🔐 Autenticación

```http
POST /api/token/
POST /api/token/refresh/
POST /api/users/guest-access/
POST /api/users/send-otp/
POST /api/users/verify-otp/
```

### 👥 Usuarios

```http
POST /api/users/register-consumer/
GET  /api/users/consumer-profile/
PUT  /api/users/consumer-profile/
POST /api/users/change-password/
```

### 🏢 Proveedores

```http
POST /api/providers/register/
PUT  /api/providers/verification-request/
GET  /api/providers/profile/
PUT  /api/providers/profile/
```

### 📅 Citas

```http
POST /api/appointments/create/
GET  /api/appointments/consumer/
GET  /api/appointments/provider/
GET  /api/appointments/{id}/
PATCH /api/appointments/{id}/status/
POST /api/appointments/{id}/cancel/
POST /api/appointments/{id}/mark-paid/
```

### 🛠️ Servicios

```http
POST /api/services/create/
GET  /api/services/
GET  /api/services/provider/
GET  /api/services/{id}/
PUT  /api/services/{id}/
DELETE /api/services/{id}/
```

### 📍 Direcciones

```http
GET  /api/addresses/
POST /api/addresses/
GET  /api/addresses/{id}/
PUT  /api/addresses/{id}/
DELETE /api/addresses/{id}/
```

## 🛠️ Tecnologías

### Backend

- **Django 5.2+** - Framework web
- **Django REST Framework 3.16+** - API REST
- **Django CORS Headers** - Manejo de CORS
- **Django Filter** - Filtrado de datos
- **DRF Simple JWT** - Autenticación JWT
- **DRF YASG** - Documentación Swagger

### Base de Datos

- **PostgreSQL 13+** - Base de datos principal
- **Cache Local** - OTP y sesiones (Django cache framework)

### Testing

- **Coverage** - Cobertura de código
- **Pytest** - Framework de testing
- **Factory Boy** - Generación de datos de prueba

### DevOps

- **Docker** - Contenedores
- **Docker Compose** - Orquestación
- **Gunicorn** - Servidor WSGI

## 📈 Estado del Proyecto

### ✅ Completado

- [x] Sistema de autenticación JWT
- [x] Gestión de usuarios y perfiles
- [x] Sistema de OTP
- [x] Registro de consumidores y proveedores
- [x] Sistema de citas
- [x] Gestión de servicios
- [x] Sistema de pagos básico
- [x] Almacenamiento de imágenes
- [x] Gestión de direcciones
- [x] Tests unitarios y de integración
- [x] Documentación API (Swagger)
- [x] Configuración Docker

### 🚧 En Desarrollo

- [ ] Sistema de notificaciones push
- [ ] Integración con pasarelas de pago
- [ ] Sistema de calificaciones y reseñas
- [ ] Reportes y analytics avanzados
- [ ] API para aplicaciones móviles

### 📋 Pendiente

- [ ] Tests de performance
- [ ] Tests de seguridad
- [ ] CI/CD pipeline
- [ ] Monitoreo y logging
- [ ] Documentación de deployment

## 🤝 Contribución

### Cómo Contribuir

1. **Fork** el proyecto
2. **Crea** una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abre** un Pull Request

### Estándares de Código

- **Python**: PEP 8
- **Django**: Django Coding Style
- **Tests**: Cobertura mínima 80%
- **Documentación**: Docstrings en español

### Reportar Bugs

Usa el sistema de [Issues](https://github.com/tu-usuario/homeService_API/issues) para reportar bugs o solicitar features.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 📞 Soporte

- **Email**: soporte@homeservice.com
- **Documentación**: [Wiki del proyecto](https://github.com/tu-usuario/homeService_API/wiki)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/homeService_API/issues)

---

<div align="center">

**Desarrollado con ❤️ para conectar servicios domésticos en Ecuador**

[![HomeService](https://img.shields.io/badge/HomeService-API-blue?style=for-the-badge&logo=home)](https://github.com/tu-usuario/homeService_API)

</div>


