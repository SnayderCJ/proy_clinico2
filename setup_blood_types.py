"""
Script para agregar los tipos de sangre al sistema.
Ejecutar con: python manage.py shell < setup_blood_types.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proy_clinico.settings')
django.setup()

from applications.core.models import TipoSangre

def create_blood_types():
    """Crear tipos de sangre básicos"""
    blood_types_data = [
        {'tipo': 'A+', 'descripcion': 'Tipo A positivo - Puede recibir de: A+, A-, O+, O-'},
        {'tipo': 'A-', 'descripcion': 'Tipo A negativo - Puede recibir de: A-, O-'},
        {'tipo': 'B+', 'descripcion': 'Tipo B positivo - Puede recibir de: B+, B-, O+, O-'},
        {'tipo': 'B-', 'descripcion': 'Tipo B negativo - Puede recibir de: B-, O-'},
        {'tipo': 'AB+', 'descripcion': 'Tipo AB positivo - Receptor universal'},
        {'tipo': 'AB-', 'descripcion': 'Tipo AB negativo - Puede recibir de: A-, B-, AB-, O-'},
        {'tipo': 'O+', 'descripcion': 'Tipo O positivo - Puede recibir de: O+, O-'},
        {'tipo': 'O-', 'descripcion': 'Tipo O negativo - Donante universal'}
    ]
    
    for blood_type_data in blood_types_data:
        tipo_sangre, created = TipoSangre.objects.get_or_create(
            tipo=blood_type_data['tipo'],
            defaults={'descripcion': blood_type_data['descripcion']}
        )
        if created:
            print(f"Creado tipo de sangre: {tipo_sangre.tipo}")
        else:
            print(f"Ya existe el tipo de sangre: {tipo_sangre.tipo}")

def main():
    """Función principal"""
    print("\n=== AGREGANDO TIPOS DE SANGRE ===\n")
    create_blood_types()
    print("\n=== PROCESO COMPLETADO ===")

if __name__ == "__main__":
    main()
