#!/usr/bin/env python
"""
Script de verificación para la integración de PayPal
Ejecutar: python verificar_paypal.py
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proy_clinico.settings')
django.setup()

from django.conf import settings
from applications.doctor.utils.paypal_config import validate_paypal_config
from applications.doctor.utils.paypal_validator import PayPalValidator

def verificar_configuracion():
    """Verifica la configuración de PayPal"""
    print("🔍 Verificando configuración de PayPal...")
    
    # Verificar variables de entorno
    config_errors = validate_paypal_config()
    
    if config_errors:
        print("❌ Errores de configuración encontrados:")
        for error in config_errors:
            print(f"   - {error}")
        return False
    
    print("✅ Configuración de PayPal válida")
    
    # Mostrar configuración actual
    print(f"   - Client ID: {settings.PAYPAL_CLIENT_ID[:20]}...")
    print(f"   - Mode: {settings.PAYPAL_MODE}")
    print(f"   - Debug: {settings.PAYPAL_DEBUG}")
    
    return True

def verificar_modelos():
    """Verifica que los modelos estén correctamente configurados"""
    print("\n🔍 Verificando modelos de base de datos...")
    
    try:
        from applications.doctor.models import Pago, DetallePago, ServiciosAdicionales
        from applications.doctor.utils.pago import MetodoPagoChoices, EstadoPagoChoices
        
        # Verificar que PayPal esté en las opciones
        metodos = dict(MetodoPagoChoices.choices)
        if 'paypal' not in metodos:
            print("❌ PayPal no está configurado en MetodoPagoChoices")
            return False
        
        print("✅ Modelos configurados correctamente")
        print(f"   - Métodos de pago disponibles: {list(metodos.keys())}")
        print(f"   - Estados de pago disponibles: {list(dict(EstadoPagoChoices.choices).keys())}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando modelos: {e}")
        return False

def verificar_urls():
    """Verifica que las URLs estén configuradas"""
    print("\n🔍 Verificando configuración de URLs...")
    
    try:
        from django.urls import reverse
        
        urls_requeridas = [
            'doctor:crear_pago',
            'doctor:crear_pago_api',
            'doctor:procesar_pago_paypal',
            'doctor:cancelar_pago_paypal',
            'doctor:listar_pagos',
        ]
        
        for url_name in urls_requeridas:
            try:
                reverse(url_name)
                print(f"   ✅ {url_name}")
            except:
                print(f"   ❌ {url_name} - No encontrada")
                return False
        
        print("✅ URLs configuradas correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando URLs: {e}")
        return False

def verificar_templates():
    """Verifica que los templates existan"""
    print("\n🔍 Verificando templates...")
    
    templates_requeridos = [
        'templates/doctor/pagos/crear_pago.html',
        'templates/doctor/pagos/detalle_pago.html',
        'templates/doctor/pagos/listar_pagos.html',
    ]
    
    todos_existen = True
    for template in templates_requeridos:
        if os.path.exists(template):
            print(f"   ✅ {template}")
        else:
            print(f"   ❌ {template} - No encontrado")
            todos_existen = False
    
    if todos_existen:
        print("✅ Templates encontrados")
    
    return todos_existen

def verificar_conexion_paypal():
    """Verifica la conexión con PayPal"""
    print("\n🔍 Verificando conexión con PayPal...")
    
    try:
        validator = PayPalValidator()
        token = validator._get_access_token()
        
        if token:
            print("✅ Conexión con PayPal exitosa")
            print(f"   - Token obtenido: {token[:20]}...")
            return True
        else:
            print("❌ No se pudo obtener token de PayPal")
            print("   - Verificar credenciales y conexión a internet")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con PayPal: {e}")
        return False

def verificar_servicios():
    """Verifica que existan servicios adicionales"""
    print("\n🔍 Verificando servicios adicionales...")
    
    try:
        from applications.doctor.models import ServiciosAdicionales
        
        servicios = ServiciosAdicionales.objects.filter(activo=True)
        count = servicios.count()
        
        if count > 0:
            print(f"✅ {count} servicios adicionales encontrados")
            for servicio in servicios[:3]:  # Mostrar solo los primeros 3
                print(f"   - {servicio.nombre_servicio}: ${servicio.costo_servicio}")
            if count > 3:
                print(f"   ... y {count - 3} más")
            return True
        else:
            print("⚠️  No hay servicios adicionales configurados")
            print("   - Crear al menos un servicio para poder procesar pagos")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando servicios: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🚀 Verificación de Integración PayPal - Sistema Médico")
    print("=" * 60)
    
    verificaciones = [
        verificar_configuracion,
        verificar_modelos,
        verificar_urls,
        verificar_templates,
        verificar_servicios,
        verificar_conexion_paypal,
    ]
    
    resultados = []
    for verificacion in verificaciones:
        resultado = verificacion()
        resultados.append(resultado)
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    exitosas = sum(resultados)
    total = len(resultados)
    
    if exitosas == total:
        print("🎉 ¡Todas las verificaciones pasaron exitosamente!")
        print("✅ La integración de PayPal está lista para usar")
        print("\n📝 Próximos pasos:")
        print("   1. Ejecutar: python manage.py runserver")
        print("   2. Navegar a: /doctor/pagos/crear/")
        print("   3. Probar crear un pago con PayPal")
    else:
        print(f"⚠️  {exitosas}/{total} verificaciones exitosas")
        print("❌ Hay problemas que necesitan ser resueltos")
        print("\n🔧 Revisa los errores mostrados arriba y:")
        print("   1. Verifica la configuración en .env")
        print("   2. Ejecuta las migraciones: python manage.py migrate")
        print("   3. Crea servicios adicionales en el admin")
    
    print("\n📚 Para más información, consulta: PAYPAL_INTEGRATION_README.md")

if __name__ == "__main__":
    main()
