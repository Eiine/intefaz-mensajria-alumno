import os
import django
import random
from faker import Faker
from datetime import date, timedelta

# 1. Configuración de Entorno Django
# Asegúrate de que 'tu_proyecto' sea el nombre de tu proyecto principal de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interfas_mensajria.settings')
django.setup()

# Importar los modelos actualizados
from mensajes.models import (
    Usuario, 
    Alumno, 
    TipoNotificacion, 
    Notificacion, 
    Carrera, 
    Pago,
    Plantilla
) 

fake = Faker('es_AR') # Uso Faker para español de Argentina para datos más relevantes

# --- Datos de Soporte (Carrera, Pago, TipoNotificacion) ---

# 2. Generar Carreras
carreras_data = [
    'Ingeniería en Sistemas', 
    'Licenciatura en Administración', 
    'Abogacía', 
    'Contador Público'
]
carreras_obj = []

for nombre in carreras_data:
    carrera, created = Carrera.objects.get_or_create(nombre=nombre)
    carreras_obj.append(carrera)
print(f"✅ Creadas/obtenidas {len(carreras_obj)} Carreras.")


# 3. Generar Tipos de Notificación
tipos_notif_data = {
    'Aviso de Pago': 'Notificación de deuda o pago pendiente.',
    'Novedad Académica': 'Actualizaciones sobre fechas de exámenes o clases.',
    'Evento Institucional': 'Invitación a charlas o seminarios.',
    'Sistema': 'Alerta de mantenimiento o problema en el sistema.'
}
tipos_obj = []

for nombre, descripcion in tipos_notif_data.items():
    tipo, created = TipoNotificacion.objects.get_or_create(
        nombre=nombre,
        defaults={
            'descripcion': descripcion,
            'prioridad': random.choice(['Alta', 'Media', 'Baja']),
            'activo': True,
            'canales_permitidos': 'email,sms,push'
        }
    )
    tipos_obj.append(tipo)
print(f"✅ Creados/obtenidos {len(tipos_obj)} Tipos de Notificación.")


# 4. Generar Plantillas (una básica por TipoNotificacion y canal)
CANAL_CHOICES = ['email', 'sms', 'push']
for tipo in tipos_obj:
    for canal in CANAL_CHOICES:
        Plantilla.objects.get_or_create(
            tipo_notificacion=tipo,
            canal=canal,
            defaults={
                'tipo_evento': f'{tipo.nombre} - {canal}',
            }
        )
print("✅ Creadas Plantillas básicas.")


# --- Generación de Usuarios y Alumnos ---

NUM_ALUMNOS = 20
alumnos_creados = []
estados = ["Enviado", "Pendiente", "Error", "Leído"]

for i in range(NUM_ALUMNOS):
    
    # 5. Crear un Pago de ejemplo
    fecha_pago = fake.date_between(start_date='-1y', end_date='today')
    pago = Pago.objects.create(
        monto=fake.random_int(min=5000, max=150000, step=100) / 100,
        fecha_pago=fecha_pago
    )
    
    # 6. Crear un Usuario
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    usuario = Usuario.objects.create(
        full_name=f"{first_name} {last_name}",
        rol=random.choice(['Alumno', 'Docente']),
        carrera=random.choice(carreras_obj),
        pago=pago
    )

    # 7. Crear el Alumno (OneToOneField a Usuario)
    legajo_num = str(100000 + i) 
    
    alumno = Alumno.objects.create(
        legajo=legajo_num,
        usuario=usuario, # Asignación de OneToOneField
        fecha_ingreso=fake.date_between(start_date='-5y', end_date='-1y'),
        estado=random.choice(['Activo', 'Inactivo', 'Egresado']),
        observaciones=fake.sentence(nb_words=5),
        # Nuevo campo para el correo electrónico
        email=fake.unique.email() 
    )
    alumnos_creados.append(alumno)
    
    # 8. Generar Notificaciones para el Alumno
    num_notificaciones = random.randint(1, 5)
    for _ in range(num_notificaciones):
        tipo_notif = random.choice(tipos_obj)
        canal_elegido = random.choice(CANAL_CHOICES)
        estado_envio = random.choice(estados)
        
        # Obtenemos una plantilla que coincida con el tipo y canal
        plantilla_obj = Plantilla.objects.filter(
            tipo_notificacion=tipo_notif,
            canal=canal_elegido
        ).first()

        Notificacion.objects.create(
            usuario=usuario,
            tipo_notificacion=tipo_notif,
            canal=canal_elegido,
            estado=estado_envio,
            plantilla=plantilla_obj,
            rendered_body=fake.paragraph(nb_sentences=3),
            fecha_envio=fake.date_time_between(start_date='-30d', end_date='now')
        )

print(f"✅ Seed completado: {NUM_ALUMNOS} Usuarios/Alumnos y {Notificacion.objects.count()} Notificaciones generadas.")