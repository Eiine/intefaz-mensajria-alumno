import os
import django
import random
from faker import Faker

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interfas_mensajria.settings')  # ⚠ nombre real de tu proyecto
django.setup()

from mensajes.models import Alumno, TipoNotificacion, Notificacion

fake = Faker()

# ------------------------------
# 1️⃣ Crear tipos de notificación
# ------------------------------
tipos = ["Email", "SMS", "Push", "WhatsApp"]

for t in tipos:
    TipoNotificacion.objects.get_or_create(nombre_tipo=t)

tipos_obj = list(TipoNotificacion.objects.all())

# ------------------------------
# 2️⃣ Crear 20 alumnos dummy
# ------------------------------
alumnos = []

for _ in range(20):
    alumno = Alumno.objects.create(
    nombre=fake.first_name(),
    apellido=fake.last_name(),
    dni=str(fake.unique.random_number(digits=8, fix_len=True))[:20],
    telefono=fake.phone_number()[:20],
    direccion=fake.address()
)

    alumnos.append(alumno)

# ------------------------------
# 3️⃣ Crear notificaciones dummy
# ------------------------------
estados = ["Enviado", "Pendiente", "Error"]

for alumno in alumnos:
    # Cada alumno recibe entre 1 y 3 notificaciones aleatorias
    for _ in range(random.randint(1, 3)):
        Notificacion.objects.create(
            alumno=alumno,
            tipo=random.choice(tipos_obj),
            estado_envio=random.choice(estados)
        )

print("✅ Seed completado: 20 alumnos, tipos y notificaciones generadas")
