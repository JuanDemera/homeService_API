#!/usr/bin/env python3
"""
Script para ejecutar todos los tests de la API HomeService
Incluye tests unitarios, de integración y reportes de coverage
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando: {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Ejecutar tests de HomeService API')
    parser.add_argument('--coverage', action='store_true', help='Ejecutar con coverage')
    parser.add_argument('--html', action='store_true', help='Generar reporte HTML de coverage')
    parser.add_argument('--app', type=str, help='Ejecutar tests de una app específica')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verbose')
    parser.add_argument('--parallel', action='store_true', help='Ejecutar tests en paralelo')
    
    args = parser.parse_args()
    
    # Configurar variables de entorno para tests
    os.environ['DJANGO_SETTINGS_MODULE'] = 'backend_homeService.settings'
    os.environ['DJANGO_ENV'] = 'testing'
    
    # Comandos base
    test_command = 'python manage.py test'
    coverage_command = 'coverage run --source="." manage.py test'
    
    # Aplicar argumentos
    if args.app:
        test_command += f' {args.app}'
        coverage_command += f' {args.app}'
    
    if args.verbose:
        test_command += ' -v 2'
        coverage_command += ' -v 2'
    
    if args.parallel:
        test_command += ' --parallel'
        coverage_command += ' --parallel'
    
    print("🧪 INICIANDO TESTS DE HOMESERVICE API")
    print("="*60)
    
    # 1. Verificar instalación de dependencias
    print("\n📦 Verificando dependencias...")
    try:
        import coverage
        print("✅ coverage instalado")
    except ImportError:
        print("❌ coverage no instalado. Instalando...")
        subprocess.run("pip install coverage", shell=True, check=True)
    
    # 2. Limpiar archivos de coverage anteriores
    if args.coverage:
        print("\n🧹 Limpiando archivos de coverage anteriores...")
        subprocess.run("coverage erase", shell=True, check=False)
    
    # 3. Ejecutar tests
    if args.coverage:
        success = run_command(coverage_command, "EJECUTANDO TESTS CON COVERAGE")
    else:
        success = run_command(test_command, "EJECUTANDO TESTS")
    
    if not success:
        print("\n❌ Los tests fallaron. Revisa los errores arriba.")
        sys.exit(1)
    
    # 4. Generar reportes de coverage
    if args.coverage:
        print("\n📊 Generando reportes de coverage...")
        
        # Reporte en consola
        run_command("coverage report", "REPORTE DE COVERAGE")
        
        # Reporte HTML
        if args.html:
            run_command("coverage html", "GENERANDO REPORTE HTML")
            print("\n📁 Reporte HTML generado en: coverage_html/index.html")
    
    # 5. Mostrar resumen
    print(f"\n{'='*60}")
    print("✅ TESTS COMPLETADOS EXITOSAMENTE")
    print(f"{'='*60}")
    
    if args.coverage:
        print("📊 Se generó reporte de coverage")
        if args.html:
            print("🌐 Reporte HTML disponible en: coverage_html/index.html")
    
    print("\n🎯 Próximos pasos:")
    print("1. Revisar los tests que fallaron (si los hay)")
    print("2. Mejorar la cobertura de código si es necesario")
    print("3. Ejecutar tests de integración manualmente")
    print("4. Revisar el reporte de coverage para identificar áreas sin testear")

if __name__ == '__main__':
    main()
