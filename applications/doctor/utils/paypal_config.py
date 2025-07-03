"""
Configuración y constantes para PayPal
"""
from django.conf import settings

# Configuración de PayPal
PAYPAL_CONFIG = {
    'CLIENT_ID': getattr(settings, 'PAYPAL_CLIENT_ID', ''),
    'CLIENT_SECRET': getattr(settings, 'PAYPAL_CLIENT_SECRET', ''),
    'MODE': getattr(settings, 'PAYPAL_MODE', 'sandbox'),
    'DEBUG': getattr(settings, 'PAYPAL_DEBUG', True),
}

# URLs de PayPal según el modo
PAYPAL_URLS = {
    'sandbox': {
        'api': 'https://api.sandbox.paypal.com',
        'checkout': 'https://www.sandbox.paypal.com'
    },
    'live': {
        'api': 'https://api.paypal.com',
        'checkout': 'https://www.paypal.com'
    }
}

# Configuración del SDK de PayPal para el frontend
def get_paypal_sdk_config():
    """Retorna la configuración del SDK de PayPal para el frontend"""
    return {
        'client_id': PAYPAL_CONFIG['CLIENT_ID'],
        'currency': 'USD',
        'intent': 'capture',
        'debug': PAYPAL_CONFIG['DEBUG'],
        'locale': 'es_ES'
    }

# Validaciones de configuración
def validate_paypal_config():
    """Valida que la configuración de PayPal esté completa"""
    errors = []
    
    if not PAYPAL_CONFIG['CLIENT_ID']:
        errors.append("PAYPAL_CLIENT_ID no está configurado")
    
    if not PAYPAL_CONFIG['CLIENT_SECRET']:
        errors.append("PAYPAL_CLIENT_SECRET no está configurado")
    
    if PAYPAL_CONFIG['MODE'] not in ['sandbox', 'live']:
        errors.append("PAYPAL_MODE debe ser 'sandbox' o 'live'")
    
    return errors

# Estados de transacciones PayPal
PAYPAL_TRANSACTION_STATES = {
    'CREATED': 'Orden creada',
    'SAVED': 'Orden guardada',
    'APPROVED': 'Orden aprobada',
    'VOIDED': 'Orden anulada',
    'COMPLETED': 'Orden completada',
    'PAYER_ACTION_REQUIRED': 'Acción del pagador requerida'
}

# Códigos de error comunes de PayPal
PAYPAL_ERROR_CODES = {
    'INSTRUMENT_DECLINED': 'Instrumento de pago rechazado',
    'PAYER_CANNOT_PAY': 'El pagador no puede pagar',
    'CANNOT_BE_ZERO_OR_NEGATIVE': 'El monto no puede ser cero o negativo',
    'TRANSACTION_REFUSED': 'Transacción rechazada',
    'INTERNAL_SERVER_ERROR': 'Error interno del servidor PayPal'
}
