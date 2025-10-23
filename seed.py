# seed.py
import os
import django
import random
from faker import Faker
from datetime import datetime, timedelta
from decimal import Decimal

# ----------------------------------------
# Configuración de Django
# ----------------------------------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interfas_mensajria.settings')
django.setup()

from django.contrib.auth.models import User
from mensajes.models import Carrera, PerfilAlumno, TipoNotificacion, Notificacion, Pago, MensajeInterno

fake = Faker()

# ----------------------------------------
# Limpiar datos anteriores (opcional)
# ----------------------------------------
MensajeInterno.objects.all().delete()
Pago.objects.all().delete()
Notificacion.objects.all().delete()
TipoNotificacion.objects.all().delete()
PerfilAlumno.objects.all().delete()
Carrera.objects.all().delete()
User.objects.filter(is_superuser=False).delete()

# ----------------------------------------
# Crear Carreras
# ----------------------------------------
carreras = []
modalidades = ['Presencial', 'A distancia']
for i in range(5):
    carrera = Carrera.objects.create(
        nombre=fake.word().title(),
        modalidad=random.choice(modalidades),
        descripcion=fake.text(max_nb_chars=100)
    )
    carreras.append(carrera)

# ----------------------------------------
# Crear Usuarios y PerfilAlumno
# ----------------------------------------
alumnos = []
for i in range(10):
    user = User.objects.create_user(
        username=f"alumno{i}",
        email=f"alumno{i}@example.com",
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        password='1234'
    )
    perfil = PerfilAlumno.objects.create(
        user=user,
        dni=fake.unique.numerify(text='########'),
        telefono=fake.phone_number(),
        direccion=fake.address(),
        carrera=random.choice(carreras),
        estado_documentacion=random.choice([True, False]),
        estado_pago=random.choice([True, False])
    )
    alumnos.append(perfil)

# ----------------------------------------
# Crear Tipos de Notificación
# ----------------------------------------
tipos = []
nombres_tipos = ['Pago pendiente', 'Falta documentación', 'Clase cancelada', 'Examen', 'Recordatorio']
for nombre in nombres_tipos:
    tipo = TipoNotificacion.objects.create(nombre_tipo=nombre)
    tipos.append(tipo)

# ----------------------------------------
# Crear Notificaciones
# ----------------------------------------
for i in range(20):
    Notificacion.objects.create(
        alumno=random.choice(alumnos),
        tipo=random.choice(tipos),
        estado_envio=random.choice(['Enviado', 'Pendiente', 'Fallido']),
        mensaje=fake.text(max_nb_chars=200)
    )

# ----------------------------------------
# Crear Pagos
# ----------------------------------------
for i in range(20):
    Pago.objects.create(
        alumno=random.choice(alumnos),
        fecha_pago=fake.date_between(start_date='-1y', end_date='today'),
        monto=Decimal(f"{random.randint(1000,5000)}.00"),
        estado_pago=random.choice(['Pagado', 'Pendiente', 'Vencido']),
        descripcion=fake.text(max_nb_chars=100)
    )

# ----------------------------------------
# Crear Mensajes Internos
# ----------------------------------------
usuarios = list(User.objects.all())
for i in range(15):
    remitente, destinatario = random.sample(usuarios, 2)
    MensajeInterno.objects.create(
        remitente=remitente,
        destinatario=destinatario,
        mensaje=fake.text(max_nb_chars=200),
        leido=random.choice([True, False])
    )

print("✅ Datos de prueba generados correctamente.")
