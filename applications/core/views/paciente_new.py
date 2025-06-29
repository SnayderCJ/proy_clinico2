from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from applications.core.models import Paciente, TipoSangre, FotoPaciente
from applications.doctor.models import CitaMedica, Atencion, Pago
from applications.core.forms.paciente import PacienteForm, HistoriaClinicaForm

"""  Vista para buscar pacientes mediante AJAX. Por nombres, apellidos, cédula o teléfono. """


@login_required
@require_http_methods(["GET"])
def paciente_find(request):
    try:
        # Obtener el parámetro de búsqueda
        query = request.GET.get("q", "").strip()

        # Validar que se proporcione al menos 3 caracteres
        if len(query) < 3:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Debe proporcionar al menos 3 caracteres para la búsqueda",
                    "pacientes": [],
                }
            )

        # Construir la consulta de búsqueda
        # Buscar en nombres, apellidos, cédula, DNI y teléfono
        pacientes_query = (
            Paciente.objects.filter(
                Q(activo=True)
                & (
                    Q(nombres__icontains=query)
                    | Q(apellidos__icontains=query)
                    | Q(cedula_ecuatoriana__icontains=query)
                    | Q(dni__icontains=query)
                    | Q(telefono__icontains=query)
                )
            )
            .select_related("tipo_sangre")
            .prefetch_related(
                "atenciones__diagnostico", "atenciones__detalles__medicamento"
            )
            .order_by("apellidos", "nombres")
        )

        # Limitar resultados para mejorar rendimiento
        pacientes_query = pacientes_query[:20]

        # Convertir a lista de diccionarios
        pacientes_data = []
        for paciente in pacientes_query:
            # Calcular edad
            edad = paciente.edad

            # Obtener atenciones anteriores (últimas 10)
            atenciones = []
            for atencion in paciente.atenciones.all()[:10]:
                # Obtener prescripciones/detalles de esta atención
                detalles = []
                for detalle in atencion.detalles.all():
                    detalle_dict = {
                        "medicamento": (
                            detalle.medicamento.nombre if detalle.medicamento else None
                        ),
                        "cantidad": detalle.cantidad,
                        "prescripcion": detalle.prescripcion,
                        "duracion_tratamiento": detalle.duracion_tratamiento,
                        "frecuencia_diaria": detalle.frecuencia_diaria,
                    }
                    detalles.append(detalle_dict)

                # Obtener diagnósticos
                diagnosticos = [d.descripcion for d in atencion.diagnostico.all()]

                # Determinar tipo de consulta
                tipo_consulta = "Chequeo"
                if atencion.es_control:
                    tipo_consulta = "Control"
                elif (
                    "urgencia" in atencion.motivo_consulta.lower()
                    or "dolor" in atencion.motivo_consulta.lower()
                ):
                    tipo_consulta = "Urgencia"

                atencion_dict = {
                    "id": atencion.id,
                    "fecha_atencion": atencion.fecha_atencion.isoformat(),
                    "tipo_consulta": tipo_consulta,
                    # Signos vitales
                    "presion_arterial": atencion.presion_arterial,
                    "pulso": atencion.pulso,
                    "temperatura": (
                        float(atencion.temperatura) if atencion.temperatura else None
                    ),
                    "frecuencia_respiratoria": atencion.frecuencia_respiratoria,
                    "saturacion_oxigeno": (
                        float(atencion.saturacion_oxigeno)
                        if atencion.saturacion_oxigeno
                        else None
                    ),
                    "peso": float(atencion.peso) if atencion.peso else None,
                    "altura": float(atencion.altura) if atencion.altura else None,
                    "imc": atencion.calcular_imc,
                    # Contenido de la atención
                    "motivo_consulta": atencion.motivo_consulta,
                    "sintomas": atencion.sintomas,
                    "tratamiento": atencion.tratamiento,
                    "diagnosticos": diagnosticos,
                    "examen_fisico": atencion.examen_fisico,
                    "examenes_enviados": atencion.examenes_enviados,
                    "comentario_adicional": atencion.comentario_adicional,
                    "es_control": atencion.es_control,
                    # Prescripciones
                    "prescripciones": detalles,
                }
                atenciones.append(atencion_dict)

            paciente_dict = {
                "id": paciente.id,
                "nombres": paciente.nombres,
                "apellidos": paciente.apellidos,
                "cedula_ecuatoriana": paciente.cedula_ecuatoriana,
                "dni": paciente.dni,
                "fecha_nacimiento": (
                    paciente.fecha_nacimiento.isoformat()
                    if paciente.fecha_nacimiento
                    else None
                ),
                "edad": edad,
                "telefono": paciente.telefono,
                "email": paciente.email,
                "sexo": paciente.sexo,
                "estado_civil": paciente.estado_civil,
                "direccion": paciente.direccion,
                "latitud": float(paciente.latitud) if paciente.latitud else None,
                "longitud": float(paciente.longitud) if paciente.longitud else None,
                "tipo_sangre": (
                    paciente.tipo_sangre.tipo if paciente.tipo_sangre else None
                ),
                "foto_url": paciente.get_image,
                # Historia clínica
                "antecedentes_personales": paciente.antecedentes_personales,
                "antecedentes_quirurgicos": paciente.antecedentes_quirurgicos,
                "antecedentes_familiares": paciente.antecedentes_familiares,
                "alergias": paciente.alergias,
                "medicamentos_actuales": paciente.medicamentos_actuales,
                "habitos_toxicos": paciente.habitos_toxicos,
                "vacunas": paciente.vacunas,
                "antecedentes_gineco_obstetricos": paciente.antecedentes_gineco_obstetricos,
                # Atenciones anteriores
                "atenciones": atenciones,
                "total_atenciones": paciente.atenciones.count(),
            }
            pacientes_data.append(paciente_dict)
        print(pacientes_data)
        return JsonResponse(
            {
                "success": True,
                "pacientes": pacientes_data,
                "total": len(pacientes_data),
                "query": query,
            }
        )

    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": f"Error en la búsqueda: {str(e)}",
                "pacientes": [],
            },
            status=500,
        )


# ============================================================================
# VISTAS CRUD PARA PACIENTES
# ============================================================================


class PacienteListView(LoginRequiredMixin, ListView):
    """Vista para listar todos los pacientes activos"""

    model = Paciente
    template_name = "core/pacientes/list.html"
    context_object_name = "pacientes"
    paginate_by = 20

    def get_queryset(self):
        queryset = Paciente.objects.filter(activo=True).select_related("tipo_sangre")

        # Filtros de búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombres__icontains=search)
                | Q(apellidos__icontains=search)
                | Q(cedula_ecuatoriana__icontains=search)
                | Q(telefono__icontains=search)
            )

        # Filtro por tipo de sangre
        tipo_sangre = self.request.GET.get("tipo_sangre")
        if tipo_sangre:
            queryset = queryset.filter(tipo_sangre_id=tipo_sangre)

        # Filtro por sexo
        sexo = self.request.GET.get("sexo")
        if sexo:
            queryset = queryset.filter(sexo=sexo)

        return queryset.order_by("apellidos", "nombres")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tipos_sangre"] = TipoSangre.objects.all()
        context["search"] = self.request.GET.get("search", "")
        context["tipo_sangre_selected"] = self.request.GET.get("tipo_sangre", "")
        context["sexo_selected"] = self.request.GET.get("sexo", "")
        context["total_pacientes"] = Paciente.cantidad_pacientes()
        return context


class PacienteDetailView(LoginRequiredMixin, DetailView):
    """Vista para mostrar detalles completos de un paciente"""

    model = Paciente
    template_name = "core/pacientes/detail.html"
    context_object_name = "paciente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = self.get_object()

        # Obtener atenciones médicas recientes
        try:
            context["atenciones_recientes"] = paciente.atenciones.all()[:5]
            context["total_atenciones"] = paciente.atenciones.count()
        except:
            context["atenciones_recientes"] = []
            context["total_atenciones"] = 0

        # Obtener citas médicas recientes
        try:
            context["citas_recientes"] = paciente.citas.all()[:5]
            context["total_citas"] = paciente.citas.count()
        except:
            context["citas_recientes"] = []
            context["total_citas"] = 0

        # Obtener próximas citas
        try:
            from datetime import date

            context["proximas_citas"] = (
                paciente.citas.filter(fecha__gte=date.today())
                .exclude(estado="cancelada")
                .order_by("fecha", "hora_cita")[:3]
            )
        except:
            context["proximas_citas"] = []

        # Obtener pagos recientes
        try:
            pagos_recientes = Pago.objects.filter(atencion__paciente=paciente).order_by(
                "-fecha_creacion"
            )[:5]
            context["pagos_recientes"] = pagos_recientes
            context["total_pagos"] = Pago.objects.filter(
                atencion__paciente=paciente
            ).count()

            # Calcular total pagado
            from django.db.models import Sum

            total_pagado = (
                Pago.objects.filter(
                    atencion__paciente=paciente, estado="pagado"
                ).aggregate(total=Sum("monto_total"))["total"]
                or 0
            )
            context["total_pagado"] = total_pagado
        except:
            context["pagos_recientes"] = []
            context["total_pagos"] = 0
            context["total_pagado"] = 0

        # Obtener fotos del paciente
        try:
            context["fotos"] = paciente.fotos.all()[:6]
        except:
            context["fotos"] = []

        # Calcular estadísticas
        context["edad"] = paciente.edad
        context["imc"] = self.calcular_imc_promedio(paciente)

        return context

    def calcular_imc_promedio(self, paciente):
        """Calcula el IMC promedio basado en las últimas atenciones"""
        atenciones_con_peso = paciente.atenciones.filter(
            peso__isnull=False, altura__isnull=False
        )[:3]

        if atenciones_con_peso:
            imc_total = sum(
                [a.calcular_imc for a in atenciones_con_peso if a.calcular_imc]
            )
            return round(imc_total / len(atenciones_con_peso), 1) if imc_total else None
        return None


class PacienteCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo paciente"""

    model = Paciente
    form_class = PacienteForm
    template_name = "core/pacientes/form.html"
    success_url = reverse_lazy("core:paciente_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Paciente {self.object.nombre_completo} creado exitosamente.",
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request, "Error al crear el paciente. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class PacienteUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar datos de un paciente"""

    model = Paciente
    form_class = PacienteForm
    template_name = "core/pacientes/form.html"

    def get_success_url(self):
        return reverse_lazy("core:paciente_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Datos de {self.object.nombre_completo} actualizados exitosamente.",
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al actualizar el paciente. Verifique los datos ingresados.",
        )
        return super().form_invalid(form)


class PacienteDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar (desactivar) un paciente"""

    model = Paciente
    template_name = "core/pacientes/delete.html"
    success_url = reverse_lazy("core:paciente_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # No eliminar físicamente, solo desactivar
        self.object.activo = False
        self.object.save()
        messages.success(
            request,
            f"Paciente {self.object.nombre_completo} desactivado exitosamente.",
        )
        return redirect(self.success_url)


# ============================================================================
# VISTAS PARA HISTORIA CLÍNICA
# ============================================================================


@login_required
def paciente_historia_clinica(request, pk):
    """Vista para gestionar la historia clínica de un paciente"""
    paciente = get_object_or_404(Paciente, pk=pk, activo=True)

    if request.method == "POST":
        form = HistoriaClinicaForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Historia clínica de {paciente.nombre_completo} actualizada exitosamente.",
            )
            return redirect("core:paciente_detail", pk=paciente.pk)
        else:
            messages.error(
                request, "Error al actualizar la historia clínica. Verifique los datos."
            )
    else:
        form = HistoriaClinicaForm(instance=paciente)

    context = {
        "paciente": paciente,
        "form": form,
        "atenciones_recientes": paciente.atenciones.all()[:10],
    }

    return render(request, "core/pacientes/historia_clinica.html", context)


@login_required
def paciente_fotos(request, pk):
    """Vista para gestionar las fotos de un paciente"""
    paciente = get_object_or_404(Paciente, pk=pk, activo=True)

    if request.method == "POST":
        if "imagen" in request.FILES:
            descripcion = request.POST.get("descripcion", "")
            foto = FotoPaciente.objects.create(
                paciente=paciente,
                imagen=request.FILES["imagen"],
                descripcion=descripcion,
            )
            messages.success(request, "Foto agregada exitosamente.")
        else:
            messages.error(request, "Debe seleccionar una imagen.")

        return redirect("core:paciente_fotos", pk=paciente.pk)

    # Paginación de fotos
    fotos_list = paciente.fotos.all()
    paginator = Paginator(fotos_list, 12)  # 12 fotos por página
    page_number = request.GET.get("page")
    fotos = paginator.get_page(page_number)

    context = {"paciente": paciente, "fotos": fotos, "total_fotos": fotos_list.count()}

    return render(request, "core/pacientes/fotos.html", context)
