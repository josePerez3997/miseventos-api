"""
Script para ejecutar tests con cobertura para el proyecto Mis Eventos API
"""
import subprocess
import sys
import os
from datetime import datetime

def run_tests():
    """
    Ejecuta los tests con pytest y genera un reporte de cobertura
    """
    # Crear carpeta para reportes si no existe
    if not os.path.exists("test_reports"):
        os.makedirs("test_reports")
    
    # Fecha y hora actual para el nombre del reporte
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Usar sys.executable para asegurar que usamos el mismo Python
    python = sys.executable
    
    # Comando para ejecutar pytest con cobertura usando el módulo directamente
    cmd = [
        python, "-m", "pytest",
        "-v",  # Verbose
        "--cov=app",  # Cobertura para el paquete app
        "--cov-report=html:test_reports/coverage_html_" + timestamp,  # Reporte HTML
        "--cov-report=term",  # Reporte en terminal
        "--cov-report=xml:test_reports/coverage_" + timestamp + ".xml",  # Reporte XML
    ]
    
    # Añadir argumentos adicionales si se proporcionan
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    print("Ejecutando tests...")
    print(" ".join(cmd))
    
    # Ejecutar comando
    try:
        result = subprocess.run(cmd)
        return result.returncode
    except FileNotFoundError:
        print("ERROR: No se pudo encontrar pytest. Asegúrate de tener instaladas las dependencias:")
        print("    pip install pytest pytest-cov")
        print("O con Poetry:")
        print("    poetry add pytest pytest-cov --dev")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())