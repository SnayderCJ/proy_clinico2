from datetime import timezone
import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from proy_clinico.settings import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_MODE

from applications.doctor.models import Pago, DetallePago, Atencion, ServiciosAdicionales
from applications.doctor.utils.pago import MetodoPagoChoices, EstadoPagoChoices
from applications.doctor.utils.doctor import DiaSemanaChoices


@login_required
def crear_pago_view(request):
    """Vista para mostrar el formulario de pago"""
    atencion_id = request.GET.get("atencion_id")
    atencion = None

    if atencion_id:
        atencion = get_object_or_404(Atencion, id=atencion_id)

    # Obtener servicios adicionales disponibles
    servicios = ServiciosAdicionales.objects.filter(activo=True)

    context = {
        "atencion": atencion,
        "servicios": servicios,
        "metodos_pago": MetodoPagoChoices.choices,
        "paypal_client_id": PAYPAL_CLIENT_ID,
        "paypal_mode": PAYPAL_MODE,
    }

    return render(request, "doctor/pagos/crear_pago.html", context)


@login_required
@csrf_exempt
def crear_pago_api(request):
    """API para crear un nuevo pago"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            atencion_id = data.get("atencion_id")
            metodo_pago = data.get("metodo_pago")
            servicios_data = data.get("servicios", [])
            nombre_pagador = data.get("nombre_pagador", "")
            observaciones = data.get("observaciones", "")

            if not metodo_pago:
                return JsonResponse(
                    {"success": False, "error": "Método de pago requerido"}, status=400
                )

            with transaction.atomic():
                # Obtener atención si se proporciona
                atencion = None
                if atencion_id:
                    atencion = get_object_or_404(Atencion, id=atencion_id)

                # Crear el pago principal
                pago = Pago.objects.create(
                    atencion=atencion,
                    metodo_pago=metodo_pago,
                    monto_total=Decimal("0.00"),  # Se calculará después
                    estado=EstadoPagoChoices.PENDIENTE,
                    nombre_pagador=nombre_pagador,
                    observaciones=observaciones,
                )

                # Crear detalles de pago
                monto_total = Decimal("0.00")
                for servicio_data in servicios_data:
                    servicio_id = servicio_data.get("servicio_id")
                    cantidad = int(servicio_data.get("cantidad", 1))
                    descuento = Decimal(str(servicio_data.get("descuento", 0)))
                    aplica_seguro = servicio_data.get("aplica_seguro", False)
                    valor_seguro = servicio_data.get("valor_seguro")
                    descripcion_seguro = servicio_data.get("descripcion_seguro", "")

                    servicio = get_object_or_404(ServiciosAdicionales, id=servicio_id)

                    # Crear detalle de pago
                    detalle = DetallePago.objects.create(
                        pago=pago,
                        servicio_adicional=servicio,
                        cantidad=cantidad,
                        precio_unitario=servicio.costo_servicio,
                        descuento_porcentaje=descuento,
                        aplica_seguro=aplica_seguro,
                        valor_seguro=(
                            Decimal(str(valor_seguro)) if valor_seguro else None
                        ),
                        descripcion_seguro=descripcion_seguro,
                    )

                    monto_total += detalle.subtotal

                # Actualizar monto total del pago
                pago.monto_total = monto_total
                pago.save()

                return JsonResponse(
                    {
                        "success": True,
                        "pago_id": pago.id,
                        "monto_total": float(pago.monto_total),
                        "mensaje": "Pago creado exitosamente",
                    }
                )

        except Exception as e:
            return JsonResponse(
                {"success": False, "error": f"Error creando pago: {str(e)}"}, status=500
            )

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
@csrf_exempt
def procesar_pago_paypal(request):
    """API para procesar pago con PayPal"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            pago_id = data.get("pago_id")
            paypal_order_id = data.get("paypal_order_id")
            paypal_payer_id = data.get("paypal_payer_id")

            if not all([pago_id, paypal_order_id]):
                return JsonResponse(
                    {"success": False, "error": "Datos de PayPal incompletos"},
                    status=400,
                )

            # Obtener el pago
            pago = get_object_or_404(Pago, id=pago_id)

            # Actualizar el pago con información de PayPal
            pago.estado = EstadoPagoChoices.PAGADO
            pago.fecha_pago = timezone.now()
            pago.referencia_externa = paypal_order_id
            pago.observaciones = f"PayPal Order ID: {paypal_order_id}, Payer ID: {paypal_payer_id}. {pago.observaciones or ''}"
            pago.save()

            return JsonResponse(
                {
                    "success": True,
                    "mensaje": "Pago procesado exitosamente con PayPal",
                    "pago_id": pago.id,
                    "estado": pago.estado,
                }
            )

        except Exception as e:
            return JsonResponse(
                {"success": False, "error": f"Error procesando pago: {str(e)}"},
                status=500,
            )

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
@csrf_exempt
def cancelar_pago_paypal(request):
    """API para manejar cancelación de pago PayPal"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            pago_id = data.get("pago_id")

            if not pago_id:
                return JsonResponse(
                    {"success": False, "error": "ID de pago requerido"}, status=400
                )

            # Obtener el pago
            pago = get_object_or_404(Pago, id=pago_id)

            # Actualizar estado a cancelado
            pago.estado = EstadoPagoChoices.CANCELADO
            pago.observaciones = (
                f"Pago cancelado por el usuario. {pago.observaciones or ''}"
            )
            pago.save()

            return JsonResponse(
                {"success": True, "mensaje": "Pago cancelado", "pago_id": pago.id}
            )

        except Exception as e:
            return JsonResponse(
                {"success": False, "error": f"Error cancelando pago: {str(e)}"},
                status=500,
            )

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def listar_pagos(request):
    """Vista para listar todos los pagos"""
    pagos = Pago.objects.filter(activo=True).order_by("-fecha_creacion")

    # Filtros opcionales
    estado = request.GET.get("estado")
    if estado:
        pagos = pagos.filter(estado=estado)

    metodo = request.GET.get("metodo")
    if metodo:
        pagos = pagos.filter(metodo_pago=metodo)

    context = {
        "pagos": pagos,
        "estados": EstadoPagoChoices.choices,
        "metodos": MetodoPagoChoices.choices,
    }

    return render(request, "doctor/pagos/listar_pagos.html", context)


@login_required
def detalle_pago(request, pago_id):
    """Vista para ver el detalle de un pago"""
    pago = get_object_or_404(Pago, id=pago_id)
    detalles = DetallePago.objects.filter(pago=pago)

    context = {"pago": pago, "detalles": detalles}

    return render(request, "doctor/pagos/detalle_pago.html", context)
