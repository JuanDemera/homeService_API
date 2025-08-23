#!/usr/bin/env python3
"""
Script para instalar dependencias necesarias para testing de HomeService API
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Comando ejecutado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando: {command}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Se requiere Python 3.8 o superior")
        print(f"Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True

def install_dependencies():
    """Instalar dependencias de testing"""
    dependencies = [
        "coverage>=7.0.0",
        "pytest>=7.0.0",
        "pytest-django>=4.5.0",
        "pytest-cov>=4.0.0",
        "factory-boy>=3.2.0",
        "faker>=18.0.0"
    ]
    
    print("\n🔧 Instalando dependencias de testing...")
    
    for dep in dependencies:
        print(f"\n📦 Instalando {dep}...")
        if not run_command(f"pip install {dep}", f"Instalando {dep}"):
            print(f"⚠️  No se pudo instalar {dep}")
    
    print("\n✅ Instalación de dependencias completada")

def verify_installation():
    """Verificar que las dependencias se instalaron correctamente"""
    print("\n🔍 Verificando instalación...")
    
    try:
        import coverage
        print("✅ coverage instalado correctamente")
    except ImportError:
        print("❌ coverage no está instalado")
        return False
    
    try:
        import pytest
        print("✅ pytest instalado correctamente")
    except ImportError:
        print("❌ pytest no está instalado")
        return False
    
    try:
        import factory
        print("✅ factory-boy instalado correctamente")
    except ImportError:
        print("❌ factory-boy no está instalado")
        return False
    
    return True

def create_test_config():
    """Crear configuración de testing si no existe"""
    print("\n⚙️  Verificando configuración de testing...")
    
    # Verificar si existe .coveragerc
    if not os.path.exists('.coveragerc'):
        print("📝 Creando archivo .coveragerc...")
        with open('.coveragerc', 'w') as f:
            f.write("""[run]
source = .
omit = 
    */migrations/*
    */tests/*
    */venv/*
    */__pycache__/*
    manage.py
    */settings.py
    */wsgi.py
    */asgi.py
    */urls.py
    */admin.py
    */apps.py
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod
    def main\(\):
    def test_.*:
    class Test.*:
    def setUp\(\):
    def tearDown\(\):
    def setUpClass\(\):
    def tearDownClass\(\):

[html]
directory = coverage_html
""")
        print("✅ Archivo .coveragerc creado")
    else:
        print("✅ Archivo .coveragerc ya existe")

def main():
    """Función principal"""
    print("🧪 CONFIGURACIÓN DE TESTING - HOMESERVICE API")
    print("="*60)
    
    # 1. Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # 2. Instalar dependencias
    install_dependencies()
    
    # 3. Verificar instalación
    if not verify_installation():
        print("\n❌ Algunas dependencias no se instalaron correctamente")
        sys.exit(1)
    
    # 4. Crear configuración
    create_test_config()
    
    # 5. Mostrar resumen
    print(f"\n{'='*60}")
    print("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
    print(f"{'='*60}")
    
    print("\n🎯 Próximos pasos:")
    print("1. Ejecutar tests: python run_tests.py --coverage")
    print("2. Ver reporte: coverage html")
    print("3. Abrir reporte: coverage_html/index.html")
    
    print("\n📚 Documentación:")
    print("- TESTING.md - Guía completa de testing")
    print("- TEST_SUMMARY.md - Resumen de tests implementados")
    
    print("\n🚀 Comandos útiles:")
    print("- python run_tests.py --help")
    print("- python manage.py test --help")
    print("- coverage report --show-missing")

if __name__ == '__main__':
    main()
