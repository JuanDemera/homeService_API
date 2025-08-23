#!/usr/bin/env python
"""
Script para ejecutar Tests de Aceptación
========================================

Este script ejecuta los tests de aceptación de la aplicación homeService_API,
validando los flujos completos de negocio desde la perspectiva del usuario final.

Uso:
    python run_acceptance_tests.py

Requisitos:
    - Base de datos PostgreSQL configurada
    - Migraciones aplicadas
    - Variables de entorno configuradas
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line


def setup_django():
    """Configurar Django para los tests"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_homeService.settings')
    django.setup()


def run_acceptance_tests():
    """Ejecutar todos los tests de aceptación"""
    
    print(" Iniciando Tests de Aceptación - homeService_API")
    print("=" * 60)
    
    # Configurar Django
    setup_django()
    
    # Configurar el runner de tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True, keepdb=False)
    
    # Lista de tests de aceptación a ejecutar
    test_labels = [
        'acceptance_tests.UserRegistrationAcceptanceTest',
        'acceptance_tests.ProviderVerificationAcceptanceTest', 
        'acceptance_tests.ServiceManagementAcceptanceTest',
        'acceptance_tests.AppointmentBookingAcceptanceTest',
        'acceptance_tests.AdminManagementAcceptanceTest'
    ]
    
    print(f" Ejecutando {len(test_labels)} suites de tests de aceptación:")
    for i, test_label in enumerate(test_labels, 1):
        test_name = test_label.split('.')[-1]
        print(f"   {i}. {test_name}")
    
    print("\n Iniciando ejecución...")
    print("-" * 60)
    
    # Ejecutar tests
    failures = test_runner.run_tests(test_labels)
    
    print("-" * 60)
    if failures:
        print(f" Tests completados con {failures} fallos")
        return False
    else:
        print(" Todos los tests de aceptación pasaron exitosamente!")
        return True


def run_specific_test(test_name):
    """Ejecutar un test específico"""
    
    setup_django()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True, keepdb=False)
    
    print(f" Ejecutando test específico: {test_name}")
    print("-" * 60)
    
    failures = test_runner.run_tests([f'acceptance_tests.{test_name}'])
    
    if failures:
        print(f" Test {test_name} falló")
        return False
    else:
        print(f" Test {test_name} pasó exitosamente!")
        return True


def main():
    """Función principal"""
    
    if len(sys.argv) > 1:
        
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        
        success = run_acceptance_tests()
    
   
    print("\n" + "=" * 60)
    print(" RESUMEN DE TESTS DE ACEPTACIÓN")
    print("=" * 60)
    
    if success:
        print(" RESULTADO: ÉXITO TOTAL")
        print(" Todos los flujos de negocio funcionan correctamente")
        print(" La aplicación está lista para producción")
    else:
        print(" RESULTADO: REQUIERE ATENCIÓN") 
        print(" Algunos flujos de negocio presentan problemas")
        print(" Revisar y corregir los errores reportados")
    
    print("=" * 60)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
