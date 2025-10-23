from django.http import JsonResponse
from .models import PerfilAlumno, TipoNotificacion, Notificacion, Pago, MensajeInterno
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PerfilAlumnoForm, NotificacionForm, CarreraForm, PagoForm, MensajeInternoForm

def interfaz(request):
    # Obtener datos de query parameters
    nombre = request.GET.get('nombre', '')
    email = request.GET.get('email', '')
    alerta = request.GET.get('alerta', '')

    context = {
        'nombre': nombre,
        'email': email,
        'alerta': alerta
    }

    return render(request, 'mensajes/interfaz.html', context)


def notificaciones(request):
    # Obtener datos de query parameters
    nombre = request.GET.get('nombre', '')
    email = request.GET.get('email', '')
    alerta = request.GET.get('alerta', '')

    context = {
        'nombre': nombre,
        'email': email,
        'alerta': alerta
    }

    return render(request, 'mensajes/notificaciones.html', context)

# mensajes/views.py


# ----------------------------------------
# PerfilAlumno CRUD
# ----------------------------------------

def listar_alumnos(request):
    alumnos = PerfilAlumno.objects.select_related('user', 'carrera').all()
    return render(request, 'mensajes/interfaz.html', {'alumnos': alumnos})

def filtrar_alumnos(request):
    """Filtra alumnos por tag o término de búsqueda (nombre, apellido o DNI)."""
    tag = request.GET.get('tag', '').strip().lower()
    search = request.GET.get('search', '').strip()

    alumnos = PerfilAlumno.objects.select_related('user', 'carrera').all()

    # --- Filtro por TAG ---
    if tag == 'pago':
        alumnos = alumnos.filter(estado_pago=False)
    elif tag == 'falta de documentación':
        alumnos = alumnos.filter(estado_documentacion=False)
    elif tag == 'tarea':
        alumnos = alumnos.filter(
            id__in=Notificacion.objects.filter(tipo__nombre_tipo__iexact='Tarea').values('alumno_id')
        )

    # --- Filtro por búsqueda ---
    if search:
        alumnos = alumnos.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(dni__icontains=search)
        )

    data = [
        {
            'id': a.id,
            'nombre': a.user.first_name,
            'apellido': a.user.last_name,
            'dni': a.dni,
            'telefono': a.telefono or '—',
            'direccion': a.direccion or '—',
            'carrera': a.carrera.nombre if a.carrera else 'Sin carrera',
            'estado_pago': a.estado_pago,
            'estado_documentacion': a.estado_documentacion,
        }
        for a in alumnos
    ]
    return JsonResponse({'alumnos': data})

def crear_alumno(request):
    form = PerfilAlumnoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('listar_alumnos')
    return render(request, 'mensajes/alumno_form.html', {'form': form})

def editar_alumno(request, pk):
    alumno = get_object_or_404(PerfilAlumno, pk=pk)
    form = PerfilAlumnoForm(request.POST or None, instance=alumno)
    if form.is_valid():
        form.save()
        return redirect('listar_alumnos')
    return render(request, 'mensajes/alumno_form.html', {'form': form})

def eliminar_alumno(request, pk):
    alumno = get_object_or_404(PerfilAlumno, pk=pk)
    if request.method == 'POST':
        alumno.delete()
        return redirect('listar_alumnos')
    return render(request, 'mensajes/eliminar_confirm.html', {'obj': alumno, 'tipo': 'alumno'})

# ----------------------------------------
# Similar CRUD para Notificacion
# ----------------------------------------
def listar_notificaciones(request):
    notificaciones = Notificacion.objects.all()
    return render(request, 'mensajes/notificaciones_list.html', {'notificaciones': notificaciones})

def crear_notificacion(request):
    form = NotificacionForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('listar_notificaciones')
    return render(request, 'mensajes/notificacion_form.html', {'form': form})

def editar_notificacion(request, pk):
    notificacion = get_object_or_404(Notificacion, pk=pk)
    form = NotificacionForm(request.POST or None, instance=notificacion)
    if form.is_valid():
        form.save()
        return redirect('listar_notificaciones')
    return render(request, 'mensajes/notificacion_form.html', {'form': form})

def eliminar_notificacion(request, pk):
    notificacion = get_object_or_404(Notificacion, pk=pk)
    if request.method == 'POST':
        notificacion.delete()
        return redirect('listar_notificaciones')
    return render(request, 'mensajes/eliminar_confirm.html', {'obj': notificacion, 'tipo': 'notificación'})
