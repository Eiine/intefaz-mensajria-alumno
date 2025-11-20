from django.core.management.base import BaseCommand
from django.utils import timezone
from mensajes.models import Pago, Notificacion

class Command(BaseCommand):
    help = 'Verifica pagos vencidos y envía notificaciones evitando duplicados del día'

    def handle(self, *args, **kwargs):
        hoy = timezone.now().date()

        # Filtramos pagos vencidos pendientes
        pagos_vencidos = Pago.objects.filter(
            fecha_vencimiento__lt=hoy,
            estado_pago="Pendiente"
        )

        for pago in pagos_vencidos:
            # Verificamos si ya existe una notificación de "Pago vencido" para hoy
            notificacion_existente = Notificacion.objects.filter(
                usuario=pago.usuario,
                titulo="Pago vencido",
                fecha_envio__date=hoy  # asumiendo que Notificacion tiene un campo fecha_envio
            ).exists()

            if not notificacion_existente:
                # Crear notificación si no existe
                Notificacion.objects.create(
                    usuario=pago.usuario,
                    titulo="Pago vencido",
                    mensaje="Tenés un pago vencido. Por favor regularizá tu situación."
                )
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Notificación enviada al usuario {pago.usuario.id}"
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"⚠️ Usuario {pago.usuario.id} ya fue notificado hoy"
                ))

#comando para agregar la tarea a los cron del sistema linux server
#python manage.py crontab add
#si se modificara el cron en algun momento se debera ejecutar los siguientes comandos
#python manage.py crontab remove
#python manage.py crontab add
