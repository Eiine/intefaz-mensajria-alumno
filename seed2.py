import os
import django

# 1️⃣ Configurar el entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interfas_mensajria.settings')
django.setup()

# 2️⃣ Importar modelos
from django.contrib.auth.models import User
from mensajes.models import MensajeInterno  # Asegurate que tu app se llame "mensajes"

def seed_mensajes():
    # Buscar usuario administrador
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("⚠️ No hay usuario administrador para enviar los mensajes.")
        return

    # Crear mensajes para todos los usuarios
    for user in User.objects.exclude(id=admin_user.id):
        MensajeInterno.objects.create(
            remitente=admin_user,
            destinatario=user,
            mensaje=f"Hola {user.username}, este es un mensaje de prueba del sistema."
        )
        print(f"📩 Mensaje enviado a {user.username}")

    print("✅ Seed de mensajes completado.")

if __name__ == "__main__":
    seed_mensajes()
