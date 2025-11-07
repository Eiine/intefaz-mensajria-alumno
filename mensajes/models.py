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

    nombre = models.CharField(max_length=100)
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

    def __str__(self):
        return self.nombre_tipo

# ----------------------------------------
# Tabla: Notificacion
# ----------------------------------------
class Notificacion(models.Model):
    alumno = models.ForeignKey(PerfilAlumno, on_delete=models.CASCADE)
    tipo = models.ForeignKey(TipoNotificacion, on_delete=models.CASCADE)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado_envio = models.CharField(max_length=50)  # "Enviado", "Fallido", "Pendiente"
    mensaje = models.TextField(default="mensaje por defecto")

    def __str__(self):
        return f"Notificación {self.tipo} para {self.alumno}"

# ----------------------------------------
# Tabla: Pago
# ----------------------------------------
class Pago(models.Model):
    alumno = models.ForeignKey(PerfilAlumno, on_delete=models.CASCADE)
    fecha_pago = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado_pago = models.CharField(max_length=20)  # "Pagado", "Pendiente", "Vencido"
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pago de {self.alumno} - {self.estado_pago} - {self.monto}"

# ----------------------------------------
# Tabla: MensajeInterno
# ----------------------------------------
from django.db import models
from django.contrib.auth.models import User

class MensajeInterno(models.Model):
    remitente = models.ForeignKey('PerfilAlumno', on_delete=models.CASCADE, related_name='mensajes_enviados')
    destinatario = models.ForeignKey('PerfilAlumno', on_delete=models.CASCADE, related_name='mensajes_recibidos')
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"De {self.remitente} a {self.destinatario}: {self.mensaje[:30]}"

