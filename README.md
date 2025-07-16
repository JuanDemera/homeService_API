# HomeService\_API

Este proyecto corresponde al backend de HomeServiceAPP, desarrollado con Django y Docker.

## 🔧 Cómo iniciar el proyecto

### 1. Levantar el contenedor de la base de datos

```bash
docker-compose up -d
```

### 2. Crear un entorno virtual para Python

**En Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**En Linux o macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

Para actualizar el archivo `requirements.txt` con los paquetes instalados:

```bash
pip freeze > requirements.txt
```

### 4. Aplicar migraciones

> **Importante:** Dado que se utiliza un modelo de usuario personalizado en la app `core`, se debe realizar primero la migración de dicha app antes de ejecutar el resto.

**Migrar `core` primero:**

```bash
python manage.py makemigrations core
python manage.py migrate core
```

**Luego aplicar el resto de migraciones:**

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Levantar el servidor de desarrollo

```bash
python manage.py runserver
```

---

Accede al proyecto en: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
Accede a la GUI en : [http://127.0.0.1:8000/swagger](http://127.0.0.1:8000/swagger)


