from django.http import JsonResponse
from .models import PerfilAlumno, TipoNotificacion,MensajeInterno ,Notificacion, Pago
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PerfilAlumnoForm ,NotificacionForm, CarreraForm, PagoForm, MensajeInternoForm,PerfilAlumno
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
import json
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Preferencia
from django.utils.timezone import localtime
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
def alumnos_lista(request):
    alumnos = User.objects.select_related("perfilalumno").all()
    data = alumnos.values("id", "first_name", "last_name", "perfilalumno__dni")
    return JsonResponse({"alumnos": list(data)})
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
        try:
            data = json.loads(request.body)

            alumno_id = data.get("alumno_id")
            tipo_nombre = data.get("tipo_nombre")
            canal = data.get("canal", "Email")
            mensaje = data.get("mensaje")
            estado_envio = data.get("estado_envio", "Pendiente")
            carrera_id = data.get("carrera_id")

            if not alumno_id or not tipo_nombre:
                return JsonResponse({"success": False, "error": "Datos incompletos."}, status=400)

            # ✅ Buscar el alumno
            try:
                alumno = PerfilAlumno.objects.get(id=alumno_id)
            except PerfilAlumno.DoesNotExist:
                return JsonResponse({"success": False, "error": "Alumno no encontrado."}, status=404)

            # ✅ Crear o recuperar el tipo de notificación
            tipo_notif, created = TipoNotificacion.objects.get_or_create(
                nombre_tipo=tipo_nombre,
                defaults={
                    "canal": canal,
                    "carrera_id": carrera_id
                }
            )

            # ✅ Crear la notificación
            notificacion = Notificacion.objects.create(
                tipo=tipo_notif,
                mensaje=mensaje,
                estado_envio=estado_envio
            )

            # ✅ Asociar el alumno a la notificación (ManyToMany)
            notificacion.alumnos.add(alumno)

            return JsonResponse({
                "success": True,
                "tipo": tipo_notif.nombre_tipo,
                "canal": tipo_notif.canal,
                "mensaje": mensaje,
                "alumno": str(alumno),
                "tipo_creado": created
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)

def panel_admin(request):
    # Traer todos los alumnos que no son staff
    alumnos = PerfilAlumno.objects.filter(user__is_staff=False).order_by('user__first_name')

    print(alumnos)
    # Tomar el primer alumno de la lista
    alumno_seleccionado = alumnos.first() if alumnos.exists() else None

    # Traer todas las notificaciones del alumno seleccionado
    notificaciones = []
    if alumno_seleccionado:
        notificaciones = Notificacion.objects.filter(alumnos=alumno_seleccionado).order_by('-fecha_envio')

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

    notificaciones = Notificacion.objects.filter(alumnos=alumno).order_by('-fecha_envio')
    data = [
        {
            'tipo': n.tipo.nombre_tipo if n.tipo else 'Sin tipo',
            'canal': n.tipo.canal if n.tipo else 'N/A',
            'mensaje': n.mensaje,
            'fecha_envio': n.fecha_envio.strftime('%d/%m/%Y %H:%M'),
            'estado_envio': n.estado_envio
        } for n in notificaciones
    ]
    return JsonResponse({'notificaciones': data, 'alumno': f'{alumno.user.first_name} {alumno.user.last_name}'})

def ajax_notificaciones(request, alumno_id):
    try:
        alumno = PerfilAlumno.objects.get(id=alumno_id)
    except PerfilAlumno.DoesNotExist:
        return JsonResponse({'error': 'Alumno no encontrado.'})

    notificaciones = Notificacion.objects.filter(alumnos=alumno).order_by('-fecha_envio')
    data = {
        'alumno': f"{alumno.user.first_name} {alumno.user.last_name}",
        'notificaciones': [
            {
                'tipo': n.tipo.nombre_tipo if n.tipo else 'Sin tipo',
                'canal': n.tipo.canal if n.tipo else 'N/A',
                'estado_envio': n.estado_envio,
                'fecha_envio': n.fecha_envio.strftime("%d/%m/%Y %H:%M"),
                'mensaje': n.mensaje
            } for n in notificaciones
        ]
    }
    return JsonResponse(data)

@login_required
def config(request):
    perfil = request.user.perfilalumno

    # Obtener o crear preferencias del usuario
    pref, created = Preferencia.objects.get_or_create(alumno=perfil)

    # Pasar los valores al template
    contexto = {
        "pref": pref
    }
    return render(request, 'mensajes/Configuraciones.html', contexto)
def mensajes_view(request):
    getUsuarios = PerfilAlumno.objects.select_related('user').all()
    usuarios = list(getUsuarios.values(
    'user__id',          # ID real del User
    'dni',
    'telefono',
    'user__first_name',
    'user__last_name'
))

    
    usuarios_json = json.dumps(usuarios, default=str)
    return render(request, "mensajes/mensajeria.html", {"usuarios": usuarios_json})

    
def obtener_mensajes(request):
    try:
        mensajes = MensajeInterno.objects.all().order_by("fecha_envio")
    
        data = []
        for m in mensajes:
            try:
                remitente_nombre = f"{m.remitente.user.first_name} {m.remitente.user.last_name}"
                destinatario_nombre = f"{m.destinatario.user.first_name} {m.destinatario.user.last_name}"

                data.append({
                            "id": m.id,
                            "remitente_id": m.remitente.user.id,
                            "destinatario_id": m.destinatario.user.id,
                            "remitente": remitente_nombre,
                            "destinatario": destinatario_nombre,
                            "mensaje": m.mensaje,
                            "fecha_envio": localtime(m.fecha_envio).strftime("%Y-%m-%d %H:%M"),
                            "leido": m.leido
                            })

            except PerfilAlumno.DoesNotExist:
                continue

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required

def enviar_mensaje(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    try:
        data = json.loads(request.body)
        destinatario_id = data.get("destinatario_id")
        mensaje_texto = data.get("mensaje")

        if not destinatario_id or not mensaje_texto:
            return JsonResponse({"error": "Datos incompletos."}, status=400)

        # Obtenemos o creamos el perfil del remitente
        remitente_perfil, _ = PerfilAlumno.objects.get_or_create(user=request.user)

        # Obtenemos o creamos el perfil del destinatario
        destinatario_usuario = User.objects.get(id=destinatario_id)
        destinatario_perfil, _ = PerfilAlumno.objects.get_or_create(user=destinatario_usuario)

        # Creamos el mensaje
        nuevo_mensaje = MensajeInterno.objects.create(
            remitente=remitente_perfil,
            destinatario=destinatario_perfil,
            mensaje=mensaje_texto
        )

        return JsonResponse({
    "success": True,
    "mensaje": "Mensaje enviado correctamente.",
    "id": nuevo_mensaje.id,
    "mensaje_texto": nuevo_mensaje.mensaje,
    "remitente": request.user.get_full_name()  # o request.user.username
})

    except User.DoesNotExist:
        return JsonResponse({"error": "El destinatario no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def actualizar_preferencia(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Obtener el perfil del alumno
            perfil = request.user.perfilalumno

            # Obtener o crear la Preferencia
            pref, created = Preferencia.objects.get_or_create(alumno=perfil)

            # Actualizar campos según los datos recibidos
            pref.tareas_pendientes = data.get("config_tareas", pref.tareas_pendientes)
            pref.calificaciones_publicadas = data.get("config_calificaciones", pref.calificaciones_publicadas)
            pref.eventos_academicos = data.get("config_eventos", pref.eventos_academicos)
            pref.anuncios_profesor = data.get("config_anuncios", pref.anuncios_profesor)
            pref.habilitar_agrupadas = data.get("config_agrupadas", pref.habilitar_agrupadas)
            pref.aplicacion_movil = data.get("canal_movil", pref.aplicacion_movil)
            pref.prioridad_notificaciones = data.get("prioridad", pref.prioridad_notificaciones)

            # Guardar cambios
            pref.save()

            return JsonResponse({"success": True, "created": created})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido"})
    
def mensajes_nuevos(request):
    try:
        usuario_actual = request.user

        # Contar mensajes no leídos donde el usuario actual es destinatario,
        # pero ignorar los mensajes que él mismo haya enviado.
        cantidad_nuevos = MensajeInterno.objects.filter(
            destinatario__user=usuario_actual,
            leido= False
        ).exclude(remitente__user=usuario_actual).count()
        print(cantidad_nuevos)
        return JsonResponse({"nuevos": cantidad_nuevos})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def marcar_leidos(request):
    if request.method == "POST":
        data = json.loads(request.body)
        remitente_user_id = data.get("remitente_id")
        usuario_actual = request.user.perfilalumno

        try:
            remitente_perfil = PerfilAlumno.objects.get(user__id=remitente_user_id)
        except PerfilAlumno.DoesNotExist:
            return JsonResponse({"error": "Remitente no encontrado."}, status=404)

        # ✅ Marcar como leídos los mensajes recibidos desde ese remitente
        MensajeInterno.objects.filter(
            remitente=remitente_perfil,
            destinatario=usuario_actual,
            leido=False
        ).update(leido=True)

        # Contar los no leídos restantes
        total_no_leidos = MensajeInterno.objects.filter(
            destinatario=usuario_actual,
            leido=False
        ).count()

        return JsonResponse({"success": True, "total_no_leidos": total_no_leidos})

    return JsonResponse({"success": False, "error": "Método no permitido"})


from django.shortcuts import render
from .models import Carrera, PerfilAlumno, TipoNotificacion, Notificacion, Pago, MensajeInterno, Preferencia


def circular(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body)
        mensaje = data.get("mensaje")
        carrera_nombre = data.get("carrera")
        nombre_tipo = data.get("nombre_tipo")  # 👈 NUEVO (dinámico)

        if not nombre_tipo:
            return JsonResponse({"error": "nombre_tipo no enviado"}, status=400)

        if not mensaje or not carrera_nombre:
            return JsonResponse({"error": "Datos incompletos"}, status=400)

        # Buscar carrera
        carrera = None
        alumnos = PerfilAlumno.objects.all()

        if carrera_nombre != "Todas":
            carrera = Carrera.objects.filter(nombre=carrera_nombre).first()
            if not carrera:
                return JsonResponse({"error": "La carrera no existe"}, status=400)
            alumnos = alumnos.filter(carrera=carrera)

        # Crear TipoNotificacion dinámico
        tipo = TipoNotificacion.objects.create(
            nombre_tipo=nombre_tipo,   # 👈 AQUÍ VA LO DINÁMICO
            canal="Email",
            carrera=carrera
        )

        # Crear Notificación
        notif = Notificacion.objects.create(
            tipo=tipo,
            estado_envio="Pendiente",
            mensaje=mensaje,
        )

        notif.alumnos.set(alumnos)

        return JsonResponse({"ok": True, "id": notif.id})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def panel_general(request):
    context = {
        'carreras': Carrera.objects.all(),
        'alumnos': PerfilAlumno.objects.all(),
        'tipos_notificacion': TipoNotificacion.objects.all(),
        'notificaciones': Notificacion.objects.all(),
        'pagos': Pago.objects.all(),
        'mensajes': MensajeInterno.objects.all(),
        'preferencias': Preferencia.objects.all(),
    }
    comprobacion = list(MensajeInterno.objects.all())
    return render(request, 'mensajes/panel_general.html', context)
