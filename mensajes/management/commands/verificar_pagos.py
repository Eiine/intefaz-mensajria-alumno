from django.core.management.base import BaseCommand
from django.utils import timezone
from mensajes.models import Pago, Notificacion

class Command(BaseCommand):
    help = 'Verifica pagos vencidos y envía notificaciones'

    def handle(self, *args, **kwargs):
        hoy = timezone.now().date()

        pagos_vencidos = Pago.objects.filter(
            fecha_vencimiento__lt=hoy,
            estado_pago="Pendiente"
        )

        for pago in pagos_vencidos:
            # Crear notificación
            Notificacion.objects.create(
                usuario=pago.usuario,
                titulo="Pago vencido",
                mensaje="Tenés un pago vencido. Por favor regularizá tu situación."
            )

            self.stdout.write(self.style.SUCCESS(
                f"Notificación enviada al usuario {pago.usuario.id}"
            ))

#comando para agregar la tarea a los cron del sistema linux server
#python manage.py crontab add
#si se modificara el cron en algun momento se debera ejecutar los siguientes comandos
#python manage.py crontab remove
#python manage.py crontab add
