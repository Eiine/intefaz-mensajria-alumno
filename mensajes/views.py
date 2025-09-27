from django.shortcuts import render
from .models import Alumno 
from django.http import JsonResponse

def inicio(request):
    alumnos = Alumno.objects.all().order_by('nombre')  
    return render(request, 'mensajes/inicio.html', {'alumnos': alumnos})

def filtrar_alumnos(request):
    num_alertas = int(request.GET.get('alerta', 0))
    
    alumnos = Alumno.objects.all()
    alumnos_filtrados = [
        {
            "nombre": a.nombre,
            "apellido": a.apellido,
            "dni": a.dni,
            "direccion": a.direccion,
            "telefono": a.telefono,
            "notificaciones": a.notificacion_set.count()
        }
        for a in alumnos if a.notificacion_set.count() == num_alertas
    ]
    
    return JsonResponse({"alumnos": alumnos_filtrados})


def formulario_alumno(request):
    if request.method == 'POST':
        # Aquí podrías procesar los datos del formulario
        alumno = request.POST.get('alumno')
        fecha = request.POST.get('fecha')
        estado = request.POST.get('estado')
        alerta = request.POST.get('alerta')
        comentario = request.POST.get('comentario')
        # Por ahora solo los imprimimos en consola (para probar)
        print(alumno, fecha, estado, alerta, comentario)
        # Opcional: enviar un mensaje de éxito
        return render(request, 'mensajes/formulario_alumno.html', {'mensaje': 'Datos guardados correctamente!'})

    return render(request, 'mensajes/formulario_alumno.html')

def detalle_alumno(request):
    # Ejemplo con datos simulados
    # Si tienes un modelo: alumno = get_object_or_404(Alumno, id=alumno_id)
    alumno = {
        'nombre': 'Juan',
        'apellido': 'Pérez',
        'estado': 'pendiente',  # puede ser 'pagada', 'pendiente' o 'vencida'
        'comentario': 'Alumno con retrasos en pagos, pendiente de completar documentación.'
    }
    return render(request, 'mensajes/detalle_alumno.html', {'alumno': alumno})

def formulario_email(request):
    # Obtener datos de query parameters
    nombre = request.GET.get('nombre', '')
    email = request.GET.get('email', '')
    alerta = request.GET.get('alerta', '')

    context = {
        'nombre': nombre,
        'email': email,
        'alerta': alerta
    }

    return render(request, 'mensajes/formulario_email.html', context)