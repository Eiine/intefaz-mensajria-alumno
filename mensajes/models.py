# ====================================================================
# MENSAJES/MODELS.PY
# Solo contiene los modelos de TU aplicación
# ====================================================================

from django.db import models
# Importamos el modelo User del sistema, NO lo redefinimos
from django.contrib.auth.models import User 
# Aunque no se usa directamente en tu código, si lo usaras, se importaría

# Opciones de Choices
CANAL_CHOICES = [
    ('email', 'Correo Electrónico'),
    ('sms', 'SMS'),
    ('push', 'Notificación Push'),
]

# --------------------------------------------------------------------
# Modelos de Soporte (Carrera, Pago, TipoNotificacion, Plantilla)
# --------------------------------------------------------------------

class Carrera(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

    class Meta:
        # Esto es importante para que Django sepa que no es una tabla del sistema
        db_table = 'mensajes_carrera'


class Pago(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField()
    
    def __str__(self):
        return f"Pago de ${self.monto} - {self.fecha_pago}"

    class Meta:
        db_table = 'mensajes_pago'


class TipoNotificacion(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    prioridad = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    canales_permitidos = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Tipos de Notificación"
        db_table = 'mensajes_tiponotificacion'


class Plantilla(models.Model):
    canal = models.CharField(max_length=10, choices=CANAL_CHOICES)
    tipo_evento = models.CharField(max_length=100)
    tipo_notificacion = models.ForeignKey(
        TipoNotificacion, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"Plantilla para {self.tipo_evento} ({self.get_canal_display()})"

    class Meta:
        db_table = 'mensajes_plantilla'

# --------------------------------------------------------------------
# Modelos Principales
# --------------------------------------------------------------------

class Usuario(models.Model):
    # NOTA: Si este 'Usuario' es el que se loguea, DEBES usar el modelo User de Django.
    # Asumo que esta es una tabla de Perfiles o Datos Adicionales.
    full_name = models.CharField(max_length=255)
    rol = models.CharField(max_length=50)
    carrera = models.ForeignKey(
        'Carrera', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    pago = models.ForeignKey(
        'Pago', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'mensajes_usuario'


class Alumno(models.Model):
    legajo = models.CharField(max_length=20, primary_key=True)
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE
    )
    fecha_ingreso = models.DateField()
    estado = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Alumno {self.legajo} - {self.usuario.full_name}"

    class Meta:
        db_table = 'mensajes_alumno'


class Notificacion(models.Model):
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE,
        related_name='notificaciones_recibidas'
    )
    tipo_notificacion = models.ForeignKey(
        TipoNotificacion, 
        on_delete=models.PROTECT
    )
    canal = models.CharField(max_length=10, choices=CANAL_CHOICES)
    id_evento_origen = models.CharField(max_length=255, blank=True, null=True)
    idempotency_key = models.CharField(max_length=255, unique=True, blank=True, null=True)
    estado = models.CharField(max_length=50)
    fecha_programada = models.DateTimeField(blank=True, null=True)
    plantilla = models.ForeignKey(
        Plantilla, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    rendered_body = models.TextField(blank=True)
    usuario_origen = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='notificaciones_enviadas'
    )
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación {self.tipo_notificacion.nombre} a {self.usuario.full_name}"

    class Meta:
        db_table = 'mensajes_notificacion'


class PreferenciasNotificaciones(models.Model):
    alumno = models.ForeignKey(
        Alumno, 
        on_delete=models.CASCADE
    )
    tipo_evento = models.ForeignKey(
        TipoNotificacion, 
        on_delete=models.CASCADE
    )
    canal = models.CharField(max_length=10, choices=CANAL_CHOICES)
    opt_in_out = models.BooleanField(default=True)
    quiet_hours_inicio = models.TimeField(blank=True, null=True)
    quiet_hours_fin = models.TimeField(blank=True, null=True)
    idioma = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = "Preferencias de Notificaciones"
        unique_together = ('alumno', 'tipo_evento')
        db_table = 'mensajes_preferenciasnotificaciones'

    def __str__(self):
        return f"Preferencia de {self.alumno.legajo} para {self.tipo_evento.nombre}"