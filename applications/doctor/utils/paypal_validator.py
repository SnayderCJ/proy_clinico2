"""
Utilidades para validación y verificación de pagos PayPal
"""
import logging
import requests
from decimal import Decimal
from django.conf import settings

logger = logging.getLogger(__name__)

class PayPalValidator:
    """Clase para validar transacciones de PayPal"""
    
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.mode = settings.PAYPAL_MODE
        self.base_url = self._get_base_url()
    
    def _get_base_url(self):
        """Obtiene la URL base según el modo (sandbox o live)"""
        if self.mode == 'live':
            return 'https://api.paypal.com'
        else:
            return 'https://api.sandbox.paypal.com'
    
    def _get_access_token(self):
        """Obtiene token de acceso de PayPal"""
        try:
            url = f"{self.base_url}/v1/oauth2/token"
            headers = {
                'Accept': 'application/json',
                'Accept-Language': 'en_US',
            }
            data = 'grant_type=client_credentials'
            
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.client_secret),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('access_token')
            else:
                logger.error(f"Error obteniendo token PayPal: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Excepción obteniendo token PayPal: {str(e)}")
            return None
    
    def verify_payment(self, order_id, expected_amount):
        """
        Verifica un pago de PayPal
        
        Args:
            order_id (str): ID de la orden de PayPal
            expected_amount (Decimal): Monto esperado del pago
            
        Returns:
            dict: Resultado de la verificación
        """
        try:
            access_token = self._get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'error': 'No se pudo obtener token de acceso'
                }
            
            # Obtener detalles de la orden
            url = f"{self.base_url}/v2/checkout/orders/{order_id}"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Error consultando orden PayPal: {response.status_code}'
                }
            
            order_data = response.json()
            
            # Validar estado de la orden
            if order_data.get('status') != 'COMPLETED':
                return {
                    'success': False,
                    'error': f'Orden no completada. Estado: {order_data.get("status")}'
                }
            
            # Validar monto
            purchase_units = order_data.get('purchase_units', [])
            if not purchase_units:
                return {
                    'success': False,
                    'error': 'No se encontraron unidades de compra'
                }
            
            amount_data = purchase_units[0].get('amount', {})
            paid_amount = Decimal(amount_data.get('value', '0'))
            
            if abs(paid_amount - expected_amount) > Decimal('0.01'):
                return {
                    'success': False,
                    'error': f'Monto no coincide. Esperado: {expected_amount}, Pagado: {paid_amount}'
                }
            
            return {
                'success': True,
                'order_data': order_data,
                'verified_amount': paid_amount
            }
            
        except Exception as e:
            logger.error(f"Error verificando pago PayPal: {str(e)}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }
    
    def validate_webhook(self, headers, body):
        """
        Valida un webhook de PayPal (para implementación futura)
        
        Args:
            headers (dict): Headers de la petición
            body (str): Cuerpo de la petición
            
        Returns:
            bool: True si el webhook es válido
        """
        # Implementación futura para validar webhooks de PayPal
        # Esto permitiría recibir notificaciones automáticas de cambios de estado
        return True


def validate_paypal_payment_amount(order_data, expected_amount):
    """
    Función auxiliar para validar el monto de un pago PayPal
    
    Args:
        order_data (dict): Datos de la orden de PayPal
        expected_amount (Decimal): Monto esperado
        
    Returns:
        bool: True si el monto es válido
    """
    try:
        purchase_units = order_data.get('purchase_units', [])
        if not purchase_units:
            return False
        
        amount_data = purchase_units[0].get('amount', {})
        paid_amount = Decimal(str(amount_data.get('value', '0')))
        
        # Permitir una diferencia mínima por redondeo
        return abs(paid_amount - expected_amount) <= Decimal('0.01')
        
    except Exception as e:
        logger.error(f"Error validando monto PayPal: {str(e)}")
        return False


def log_paypal_transaction(pago_id, order_id, action, details=None):
    """
    Registra transacciones de PayPal para auditoría
    
    Args:
        pago_id (int): ID del pago en el sistema
        order_id (str): ID de la orden de PayPal
        action (str): Acción realizada (created, completed, cancelled, etc.)
        details (dict): Detalles adicionales
    """
    log_data = {
        'pago_id': pago_id,
        'paypal_order_id': order_id,
        'action': action,
        'details': details or {}
    }
    
    logger.info(f"PayPal Transaction: {log_data}")
