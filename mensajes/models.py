from django.db import models
from django.contrib.auth.models import User

# ----------------------------------------
# Tabla: Carrera
# ----------------------------------------
class Carrera(models.Model):
    MODALIDAD_CHOICES = (
        ('Presencial', 'Presencial'),
        ('A distancia', 'A distancia'),
    )

    NOMBRE_CHOICES = (
        ('Historia', 'Historia'),
        ('Matematicas', 'Matemáticas'),
        ('Informatica', 'Informática'),
        ('Medicina', 'Medicina'),
    )

    nombre = models.CharField(max_length=100, choices=NOMBRE_CHOICES)
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.modalidad})"
# ----------------------------------------
# Tabla: PerfilAlumno
# ----------------------------------------
class PerfilAlumno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    carrera = models.ForeignKey(Carrera, on_delete=models.SET_NULL, blank=True, null=True)
    estado_documentacion = models.BooleanField(default=True)  # True = completa, False = faltante
    estado_pago = models.BooleanField(default=True)  # True = al día, False = pendiente

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


# ----------------------------------------
# Tabla: TipoNotificacion
# ----------------------------------------
class TipoNotificacion(models.Model):
    nombre_tipo = models.CharField(max_length=100)
    canal = models.CharField(max_length=100, default='Email')
    fecha = models.DateField(auto_now_add=True)
    carrera = models.ForeignKey(
        'Carrera',
        on_delete=models.CASCADE,
        related_name='notificaciones',
        null=True,      # ✅ permite valores nulos
        blank=True      # ✅ no lo exige en formularios
    )

    def __str__(self):
        return f"{self.nombre_tipo} - {self.carrera.nombre if self.carrera else 'Sin carrera'}"

# ----------------------------------------
# Tabla: Notificacion
# ----------------------------------------
class Notificacion(models.Model):
    alumnos = models.ManyToManyField('PerfilAlumno')
    tipo = models.ForeignKey(TipoNotificacion, on_delete=models.CASCADE)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado_envio = models.CharField(max_length=50)  # "Enviado", "Fallido", "Pendiente","visto"
    mensaje = models.TextField(default="mensaje por defecto")

    def __str__(self):
        return f"Notificación {self.tipo} para {', '.join([str(a) for a in self.alumnos.all()])}"


# ----------------------------------------
# Tabla: Pago
# ----------------------------------------
class Pago(models.Model):
    alumno = models.ForeignKey(PerfilAlumno, on_delete=models.CASCADE)
    fecha_pago = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado_pago = models.CharField(max_length=20)  # "Pagado", "Pendiente", "Vencido"
    descripcion = models.TextField(blank=True, null=True)
    aviso_enviado = models.BooleanField(default=False)  # <-- IMPORTANTE

    def __str__(self):
        return f"Pago de {self.alumno} - {self.estado_pago} - {self.monto}"


# ----------------------------------------
# Tabla: MensajeInterno
# ----------------------------------------
class MensajeInterno(models.Model):
    remitente = models.ForeignKey('PerfilAlumno', on_delete=models.CASCADE, related_name='mensajes_enviados')
    destinatario = models.ForeignKey('PerfilAlumno', on_delete=models.CASCADE, related_name='mensajes_recibidos')
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)  # valor por defecto

    def __str__(self):
        return f"De {self.remitente} a {self.destinatario}: {self.mensaje[:30]}"


# ----------------------------------------
# Tabla: Preferencia
# ----------------------------------------
class Preferencia(models.Model):
    # --- Relación principal ---
    alumno = models.OneToOneField(
        'PerfilAlumno',
        on_delete=models.CASCADE,
        related_name='preferencias'
    )

    # --- Tipos predefinidos ---
    TIPO_CHOICES = (
        ('General', 'General'),
        ('Comunicacion', 'Comunicación'),
        ('Academica', 'Académica'),
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='General'
    )

    # --- Campo adicional para distinguir mejor ---
    motivo = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Motivo o descripción asociada a esta preferencia"
    )

    # --- Preferencias generales ---
    tareas_pendientes = models.BooleanField(default=True)
    calificaciones_publicadas = models.BooleanField(default=True)
    eventos_academicos = models.BooleanField(default=True)
    anuncios_profesor = models.BooleanField(default=True)

    # --- Notificaciones agrupadas ---
    habilitar_agrupadas = models.BooleanField(default=False)
    hora_envio_agrupadas = models.TimeField(blank=True, null=True)

    # --- Canales de entrega ---
    correo_electronico = models.BooleanField(default=True)
    aplicacion_movil = models.BooleanField(default=True)

    # --- Difusión general ---
    difusion = models.BooleanField(
        default=True,
        help_text="Indica si el alumno acepta recibir mensajes o material de difusión"
    )

    # --- Asociación con carrera (opcional) ---
    carrera = models.ForeignKey(
        'Carrera',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Carrera asociada a la preferencia (opcional)"
    )

    # --- Prioridad ---
    prioridad_notificaciones = models.PositiveIntegerField(default=50)

    # --- Fecha ---
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferencias {self.tipo} de {self.alumno}"

    class Meta:
        verbose_name = "Preferencia de Notificación"
        verbose_name_plural = "Preferencias de Notificaciones"