import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interfas_mensajria.settings')
django.setup()

from mensajes.models import Carrera

# 🔽 Tu código de seed normal a continuación 🔽

carreras = [
    {
        'nombre': 'Historia',
        'modalidad': 'Presencial',
        'descripcion': 'Estudio y análisis de los procesos históricos y sus implicancias sociales.',
    },
    {
        'nombre': 'Matematicas',
        'modalidad': 'A distancia',
        'descripcion': 'Formación en lógica, álgebra, cálculo y modelado matemático aplicado.',
    },
    {
        'nombre': 'Informatica',
        'modalidad': 'Presencial',
        'descripcion': 'Carrera orientada al desarrollo de software, redes y sistemas de información.',
    },
    {
        'nombre': 'Medicina',
        'modalidad': 'A distancia',
        'descripcion': 'Formación médica con enfoque en la investigación y la práctica clínica asistida.',
    },
]

for carrera_data in carreras:
    carrera, created = Carrera.objects.get_or_create(
        nombre=carrera_data['nombre'],
        modalidad=carrera_data['modalidad'],
        defaults={'descripcion': carrera_data['descripcion']}
    )
    if created:
        print(f'✅ Carrera creada: {carrera.nombre} ({carrera.modalidad})')
    else:
        print(f'⚠️ Carrera ya existente: {carrera.nombre} ({carrera.modalidad})')

print("🎓 Seed completado.")
