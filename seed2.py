import os
import django

# 1️⃣ Configurar el entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interfas_mensajria.settings')
django.setup()

# 2️⃣ Importar modelos
from django.contrib.auth.models import User
from mensajes.models import MensajeInterno
from mensajes.models import PerfilAlumno  # Cambia 'perfiles' por el nombre real de tu app

def seed_mensajes_admin():
    # Buscar cualquier usuario administrador
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("⚠️ No hay usuario administrador disponible.")
        return

    # Crear PerfilAlumno para admin si no existe
    admin_perfil, created = PerfilAlumno.objects.get_or_create(
        user=admin_user,
        defaults={
            'dni': '00000000',
            'telefono': '0000000000'
        }
    )
    if created:
        print(f"✅ PerfilAlumno creado para admin {admin_user.username}")

    # Crear mensajes entre admin y todos los demás usuarios
    for user in User.objects.exclude(id=admin_user.id):
        try:
            destinatario_perfil = PerfilAlumno.objects.get(user=user)

            # Mensaje de admin al usuario
            MensajeInterno.objects.create(
                remitente=admin_perfil,
                destinatario=destinatario_perfil,
                mensaje=f"Hola {user.username}, este es un mensaje de prueba del admin."
            )

            # Mensaje del usuario al admin (opcional)
            MensajeInterno.objects.create(
                remitente=destinatario_perfil,
                destinatario=admin_perfil,
                mensaje=f"Hola admin, recibí tu mensaje de prueba."
            )

            print(f"📩 Mensajes creados entre admin y {user.username}")

        except PerfilAlumno.DoesNotExist:
            print(f"⚠️ El usuario {user.username} no tiene perfil asociado, se omite.")

    print("✅ Seed de mensajes completado.")

if __name__ == "__main__":
    seed_mensajes_admin()
