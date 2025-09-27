from django.db import models

class Alumno(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class TipoNotificacion(models.Model):
    nombre_tipo = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_tipo


class Notificacion(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    tipo = models.ForeignKey(TipoNotificacion, on_delete=models.CASCADE)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado_envio = models.CharField(max_length=50)

    def __str__(self):
        return f"Notificación {self.tipo} para {self.alumno}"
