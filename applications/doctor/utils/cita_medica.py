from django.db import models

class EstadoCitaChoices(models.TextChoices):
    PENDIENTE = 'pendiente', 'Pendiente'
    CONFIRMADA = 'confirmada', 'Confirmada'
    CANCELADA = 'cancelada', 'Cancelada'
    COMPLETADA = 'completada', 'Completada'
    AUSENTE = 'ausente', 'Paciente No Asistió'
