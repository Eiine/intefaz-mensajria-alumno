from django.http import JsonResponse
from .models import PerfilAlumno, TipoNotificacion, Notificacion, Pago, MensajeInterno
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PerfilAlumnoForm, NotificacionForm, CarreraForm, PagoForm, MensajeInternoForm,PerfilAlumno
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
import json
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or '/home/'  # <- manejamos next
        user = authenticate(request, username=username, password=password)
        print(request)
        if user:
            login(request, user)
            return redirect(next_url)  # <- redirige al lugar correcto
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    # Cuando el login es GET, pasamos next al template
    next_url = request.GET.get('next', '/home/')
    return render(request, 'mensajes/login.html', {'next': next_url})
@never_cache
@login_required
def logout_view(request):
    logout(request)
    return redirect('/')
  
@login_required
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
    alumnos = PerfilAlumno.objects.select_related('user', 'carrera').all()
    return render(request, 'mensajes/notificaciones.html',{"alumnos": alumnos})

# mensajes/views.py


# ----------------------------------------
# PerfilAlumno CRUD
# ----------------------------------------
@login_required
def listar_alumnos(request):
    alumnos = PerfilAlumno.objects.select_related('user', 'carrera').all()
    return render(request, 'mensajes/interfaz.html', {'alumnos': alumnos})
@login_required
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
@login_required
def crear_alumno(request):
    form = PerfilAlumnoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('listar_alumnos')
    return render(request, 'mensajes/alumno_form.html', {'form': form})
@login_required
def editar_alumno(request, pk):
    alumno = get_object_or_404(PerfilAlumno, pk=pk)
    form = PerfilAlumnoForm(request.POST or None, instance=alumno)
    if form.is_valid():
        form.save()
        return redirect('listar_alumnos')
    return render(request, 'mensajes/alumno_form.html', {'form': form})

# ----------------------------------------
# Similar CRUD para Notificacion
# ----------------------------------------
@login_required
def listar_notificaciones(request):
    notificaciones = Notificacion.objects.all()
    return render(request, 'mensajes/notificaciones.html', {'notificaciones': notificaciones})
@login_required
def crear_notificacion(request):
    if request.method == "POST":
        data = json.loads(request.body)
        alumno_id = data.get("alumno")
        tipo_str = data.get("tipo")
        mensaje = data.get("mensaje")
        estado_envio = data.get("estado_envio", "Pendiente")

        try:
            alumno = PerfilAlumno.objects.get(id=alumno_id)
        except PerfilAlumno.DoesNotExist:
            return JsonResponse({"error": "Alumno no encontrado"}, status=400)

        tipo_notif, created = TipoNotificacion.objects.get_or_create(nombre_tipo=tipo_str)

        notificacion = Notificacion.objects.create(
            alumno=alumno,
            tipo=tipo_notif,
            mensaje=mensaje,
            estado_envio=estado_envio
        )

        return JsonResponse({
            "success": True,
            "alumno": str(alumno),
            "tipo": tipo_notif.nombre_tipo,
            "mensaje": mensaje
        })

def panel_admin(request):
    # Traer todos los alumnos que no son staff
    alumnos = PerfilAlumno.objects.filter(user__is_staff=False).order_by('user__first_name')

    print(alumnos)
    # Tomar el primer alumno de la lista
    alumno_seleccionado = alumnos.first() if alumnos.exists() else None

    # Traer todas las notificaciones del alumno seleccionado
    notificaciones = []
    if alumno_seleccionado:
        notificaciones = Notificacion.objects.filter(alumno=alumno_seleccionado).order_by('-fecha_envio')

    context = {
        'alumnos': alumnos,
        'alumno_seleccionado': alumno_seleccionado,
        'notificaciones': notificaciones,
    }

    return render(request, 'mensajes/panel_admin.html', context)

def get_notificaciones(request, alumno_id):
    try:
        alumno = PerfilAlumno.objects.get(id=alumno_id)
    except PerfilAlumno.DoesNotExist:
        return JsonResponse({'error': 'Alumno no encontrado'}, status=404)

    notificaciones = Notificacion.objects.filter(alumno=alumno).order_by('-fecha_envio')
    data = [
        {
            'tipo': n.tipo.nombre_tipo,
            'mensaje': n.mensaje,
            'fecha_envio': n.fecha_envio.strftime('%d/%m/%Y %H:%M')
        } for n in notificaciones
    ]
    return JsonResponse({'notificaciones': data, 'alumno': f'{alumno.user.first_name} {alumno.user.last_name}'})

def ajax_notificaciones(request, alumno_id):
    try:
        alumno = PerfilAlumno.objects.get(id=alumno_id)
    except PerfilAlumno.DoesNotExist:
        return JsonResponse({'error': 'Alumno no encontrado.'})

    notificaciones = Notificacion.objects.filter(alumno=alumno).order_by('-fecha_envio')
    data = {
        'alumno': f"{alumno.user.first_name} {alumno.user.last_name}",
        'notificaciones': [
            {
                'tipo': n.tipo.nombre_tipo,
                'fecha_envio': n.fecha_envio.strftime("%d/%m/%Y %H:%M"),
                'mensaje': n.mensaje
            } for n in notificaciones
        ]
    }
    return JsonResponse(data)
def api_mensajes(request, usuario_id):
    usuario = User.objects.get(id=usuario_id)

    mensajes = MensajeInterno.objects.filter(
        remitente=usuario
    ).union(
        MensajeInterno.objects.filter(destinatario=usuario)
    ).order_by('fecha_envio')

    data = [{
        'remitente': m.remitente.username,
        'destinatario': m.destinatario.username,
        'mensaje': m.mensaje,
        'fecha_envio': m.fecha_envio.strftime('%d/%m/%Y %H:%M')
    } for m in mensajes]

    return JsonResponse(data, safe=False)

@login_required
def config(request):
    return render(request, 'mensajes/Configuraciones.html')