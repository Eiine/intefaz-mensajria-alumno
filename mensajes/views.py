from datetime import datetime
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
from django.db.models import Count, Q, F, FloatField, ExpressionWrapper
from django.contrib.auth.models import User
from .models import Preferencia
from django.utils.timezone import localtime
from django.utils import timezone
from django.db.models import DateTimeField, DateField
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
    elif tag == 'Falta documentación':
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

            # Buscar el alumno
            try:
                alumno = PerfilAlumno.objects.get(id=alumno_id)
            except PerfilAlumno.DoesNotExist:
                return JsonResponse({"success": False, "error": "Alumno no encontrado."}, status=404)

            # 🛑 VALIDACIÓN: verificar si tiene notificación HOY del mismo tipo
            hoy = timezone.now().date()
            notificacion_hoy_mismo_tipo = Notificacion.objects.filter(
                alumnos=alumno,
                tipo__nombre_tipo=tipo_nombre,
                fecha_envio__date=hoy
            ).exists()

            if notificacion_hoy_mismo_tipo:
                return JsonResponse({
                    "success": False,
                    "error": f"El alumno ya recibió hoy una notificación de tipo '{tipo_nombre}'."
                }, status=409)

            # Crear o recuperar tipo de notificación
            tipo_notif, created = TipoNotificacion.objects.get_or_create(
                nombre_tipo=tipo_nombre,
                defaults={
                    "canal": canal,
                    "carrera_id": carrera_id
                }
            )

            # Crear notificación
            notificacion = Notificacion.objects.create(
                tipo=tipo_notif,
                mensaje=mensaje,
                estado_envio=estado_envio
            )

            # Asociar alumno
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

from django.db.models import Q
from mensajes.models import PerfilAlumno, Notificacion, Carrera

def panel_admin(request):
    # ═══════════════════════════════════════════════════════════════
    # PASO 1: OBTENER TODOS LOS ALUMNOS (NO STAFF)
    # ═══════════════════════════════════════════════════════════════
    alumnos = PerfilAlumno.objects.filter(user__is_staff=False).select_related('user', 'carrera')
    
    # Guardar el total antes de filtrar
    total_alumnos_sin_filtrar = alumnos.count()
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 2: APLICAR FILTROS
    # ═══════════════════════════════════════════════════════════════
    
    # FILTRO 1: Búsqueda por texto (nombre, apellido, DNI, teléfono)
    query = request.GET.get('q', '').strip()
    if query:
        alumnos = alumnos.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(dni__icontains=query) |
            Q(telefono__icontains=query) |
            Q(user__email__icontains=query)  # Bonus: también busca por email
        )
    
    # FILTRO 2: Por carrera (desplegable)
    carrera_id = request.GET.get('carrera', '').strip()
    if carrera_id:
        alumnos = alumnos.filter(carrera_id=carrera_id)
    
    # FILTRO 3: Por estado (activo/inactivo)
    estado = request.GET.get('estado', '').strip()
    if estado == 'activo':
        # Filtrar por algún campo que indique estado activo
        # Si no tienes campo 'activo', puedes usar otro criterio
        # Por ejemplo, por estado_pago o estado_documentacion
        pass  # Ajusta según tu lógica
    elif estado == 'inactivo':
        pass  # Ajusta según tu lógica
    
    # Ordenar por nombre
    alumnos = alumnos.order_by('user__first_name', 'user__last_name')
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 3: SELECCIÓN DE ALUMNO
    # ═══════════════════════════════════════════════════════════════
    
    # Si hay un alumno específico seleccionado en la URL
    alumno_id = request.GET.get('alumno_id', '')
    if alumno_id:
        try:
            alumno_seleccionado = alumnos.get(id=alumno_id)
        except PerfilAlumno.DoesNotExist:
            alumno_seleccionado = alumnos.first() if alumnos.exists() else None
    else:
        # Tomar el primer alumno de la lista filtrada
        alumno_seleccionado = alumnos.first() if alumnos.exists() else None
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 4: TRAER NOTIFICACIONES DEL ALUMNO SELECCIONADO
    # ═══════════════════════════════════════════════════════════════
    notificaciones = []
    if alumno_seleccionado:
        notificaciones = Notificacion.objects.filter(
            alumnos=alumno_seleccionado
        ).order_by('-fecha_envio')
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 5: PREPARAR DATOS PARA LOS DESPLEGABLES
    # ═══════════════════════════════════════════════════════════════
    
    # Obtener todas las carreras
    carreras = Carrera.objects.all().order_by('nombre')
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 6: CONTEXTO PARA EL TEMPLATE
    # ═══════════════════════════════════════════════════════════════
    context = {
        # Datos originales
        'alumnos': alumnos,
        'alumno_seleccionado': alumno_seleccionado,
        'notificaciones': notificaciones,
        
        # Datos nuevos para los filtros
        'carreras': carreras,
        'query': query,
        'carrera_seleccionada': carrera_id,
        'estado_seleccionado': estado,
        
        # Estadísticas útiles
        'total_alumnos': total_alumnos_sin_filtrar,
        'filtros_activos': bool(query or carrera_id or estado),
    }

    return render(request, 'mensajes/panel_admin.html', context)

# ═══════════════════════════════════════════════════════════════════
# VISTA: REPORTE DE NOTIFICACIONES POR ALUMNO
# Grupo 9 - Alumno 1: Reporte con filtros y listado de resultados
# ═══════════════════════════════════════════════════════════════════
@login_required
def reporte_notificaciones(request):
    """
    Reporte de notificaciones con filtros avanzados.
    Permite filtrar por rango de fechas, alumno, tipo de evento, estado y canal.
    Muestra indicadores y tabla de resultados.
    """
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 1: OBTENER TODAS LAS NOTIFICACIONES
    # ═══════════════════════════════════════════════════════════════
    notificaciones = Notificacion.objects.select_related(
        'tipo'
    ).prefetch_related('alumnos__user', 'alumnos__carrera')
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 2: APLICAR FILTROS
    # ═══════════════════════════════════════════════════════════════
    
    # FILTRO 1: Rango de fechas (fecha de envío)
    fecha_desde = request.GET.get('fecha_desde', '').strip()
    fecha_hasta = request.GET.get('fecha_hasta', '').strip()
    
    if fecha_desde:
        try:
            from datetime import datetime
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d')
            notificaciones = notificaciones.filter(fecha_envio__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            from datetime import datetime
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            # Agregar 23:59:59 para incluir todo el día
            fecha_hasta_obj = fecha_hasta_obj.replace(hour=23, minute=59, second=59)
            notificaciones = notificaciones.filter(fecha_envio__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # FILTRO 2: Búsqueda por alumno (nombre, apellido, DNI)
    alumno_query = request.GET.get('alumno', '').strip()
    if alumno_query:
        notificaciones = notificaciones.filter(
            Q(alumnos__user__first_name__icontains=alumno_query) |
            Q(alumnos__user__last_name__icontains=alumno_query) |
            Q(alumnos__dni__icontains=alumno_query)
        )
    
    # FILTRO 3: Tipo de evento
    tipo_evento = request.GET.get('tipo_evento', '').strip()
    if tipo_evento:
        notificaciones = notificaciones.filter(tipo_id=tipo_evento)
    
    # FILTRO 4: Estado de envío
    estado_envio = request.GET.get('estado_envio', '').strip()
    if estado_envio:
        notificaciones = notificaciones.filter(estado_envio=estado_envio)
    
    # FILTRO 5: Canal de envío (si existe en tu modelo)
    canal = request.GET.get('canal', '').strip()
    if canal:
        # Ajusta según tu modelo - puede ser tipo__canal o un campo directo
        notificaciones = notificaciones.filter(tipo__canal=canal)
    
    # Ordenar por fecha de envío descendente (más recientes primero)
    notificaciones = notificaciones.order_by('-fecha_envio')
    
    # Eliminar duplicados
    notificaciones = notificaciones.distinct()
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 3: CALCULAR INDICADORES
    # ═══════════════════════════════════════════════════════════════
    
    total_notificaciones = notificaciones.count()
    
    # Contar notificaciones fallidas
    notificaciones_fallidas = notificaciones.filter(
        estado_envio='Fallido'
    ).count()
    
    # Contar por estado
    notificaciones_enviadas = notificaciones.filter(estado_envio='Enviado').count()
    notificaciones_entregadas = notificaciones.filter(estado_envio='Entregado').count()
    notificaciones_pendientes = notificaciones.filter(estado_envio='Pendiente').count()
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 4: PREPARAR DATOS PARA FILTROS
    # ═══════════════════════════════════════════════════════════════
    
    # Obtener todos los tipos de notificación
    tipos_notificacion = TipoNotificacion.objects.all().order_by('nombre_tipo')
    
    # Opciones de estado (ajusta según tus valores reales)
    estados_disponibles = [
        ('Pendiente', 'Pendiente'),
        ('Enviado', 'Enviado'),
        ('Entregado', 'Entregado'),
        ('Fallido', 'Fallido'),
    ]
    
    # Opciones de canal (ajusta según tus valores reales)
    canales_disponibles = [
        ('Email', 'Correo Electrónico'),
        ('SMS', 'Mensaje de Texto'),
        ('WhatsApp', 'WhatsApp'),
        ('Plataforma', 'Sistema Interno'),
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 5: CONTEXTO PARA EL TEMPLATE
    # ═══════════════════════════════════════════════════════════════
    
    context = {
        'notificaciones': notificaciones,
        'total_notificaciones': total_notificaciones,
        'notificaciones_fallidas': notificaciones_fallidas,
        'notificaciones_enviadas': notificaciones_enviadas,
        'notificaciones_entregadas': notificaciones_entregadas,
        'notificaciones_pendientes': notificaciones_pendientes,
        
        # Datos para los filtros
        'tipos_notificacion': tipos_notificacion,
        'estados_disponibles': estados_disponibles,
        'canales_disponibles': canales_disponibles,
        
        # Valores de filtros aplicados
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'alumno_query': alumno_query,
        'tipo_evento': tipo_evento,
        'estado_envio': estado_envio,
        'canal': canal,
        
        # Indicador de filtros activos
        'filtros_activos': bool(fecha_desde or fecha_hasta or alumno_query or tipo_evento or estado_envio or canal),
    }
    
    return render(request, 'mensajes/reporte_notificaciones.html', context)

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
            canal="Plataforma",
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

def reporte_evento(request):
    # -------- Filtros recibidos ----------
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    carrera_id = request.GET.get("carrera")
    tipos_evento = request.GET.get("tipos")
    canal = request.GET.get("canal")

    # -------- Query base ----------
    notificaciones = Notificacion.objects.all()

    # -------- Filtros ----------
    # Filtrar por fechas
    if fecha_inicio:
        notificaciones = notificaciones.filter(fecha_envio__date__gte=fecha_inicio)
    if fecha_fin:
        notificaciones = notificaciones.filter(fecha_envio__date__lte=fecha_fin)

    # Filtrar por carrera (solo si viene un valor válido)
    if carrera_id:
        try:
            carrera_id_int = int(carrera_id)
            notificaciones = notificaciones.filter(tipo__carrera_id=carrera_id_int)
        except ValueError:
            pass  # No filtrar si viene vacío o inválido

    # Filtrar por tipo de evento (solo si viene un valor válido)
    if tipos_evento:
        try:
            tipos_evento_int = int(tipos_evento)
            notificaciones = notificaciones.filter(tipo_id=tipos_evento_int)
        except ValueError:
            pass  # No filtrar si viene vacío o inválido

    # Filtrar por canal
    if canal:
        notificaciones = notificaciones.filter(tipo__canal=canal)

    # --------- Agrupación por tipo ---------
    resumen = (
        notificaciones
        .values("tipo__nombre_tipo")
        .annotate(
            total_enviadas=Count("id"),
            total_fallidas=Count("id", filter=Q(estado_envio="Fallido"))
        )
        .order_by("tipo__nombre_tipo")
    )

    # --------- KPIs ---------
    total_enviadas = notificaciones.count()
    tipo_mayor_envios = resumen.order_by("-total_enviadas").first() if resumen else None

    # --------- Contexto para template ---------
    context = {
        "resumen": resumen,
        "total_enviadas": total_enviadas,
        "tipo_mayor_envios": tipo_mayor_envios,
        "tipos": TipoNotificacion.objects.all(),
        "carreras": Carrera.objects.all(),
        "f_fecha_inicio": fecha_inicio,
        "f_fecha_fin": fecha_fin,
        "f_carrera": carrera_id,
        "f_tipos": tipos_evento,
        "f_canal": canal,
    }

    return render(request, "mensajes/reporte_evento.html", context)
def reporte_notificaciones_por_canal(request):
    # -------- Filtros recibidos ----------
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    canal = request.GET.get("canal")
    tipo_id = request.GET.get("tipo")
    estado_envio = request.GET.get("estado_envio")

    # -------- Query base ----------
    notificaciones = Notificacion.objects.all()

    # -------- Filtros ---------
    if fecha_inicio:
        notificaciones = notificaciones.filter(fecha_envio__date__gte=fecha_inicio)
    if fecha_fin:
        notificaciones = notificaciones.filter(fecha_envio__date__lte=fecha_fin)
    if canal:
        notificaciones = notificaciones.filter(tipo__canal=canal)
    if tipo_id:
        try:
            tipo_id_int = int(tipo_id)
            notificaciones = notificaciones.filter(tipo_id=tipo_id_int)
        except ValueError:
            pass  # Ignorar si es vacío o inválido
    if estado_envio:
        notificaciones = notificaciones.filter(estado_envio=estado_envio)

    # --------- Agrupación por canal ---------
    resumen = (
        notificaciones
        .values("tipo__canal")
        .annotate(
            total_enviadas=Count("id"),
            total_fallidas=Count("id", filter=Q(estado_envio="Fallido")),
        )
        .annotate(
            porcentaje_fallo=ExpressionWrapper(
                100.0 * F("total_fallidas") / F("total_enviadas"),
                output_field=FloatField()
            )
        )
        .order_by("tipo__canal")
    )

    # --------- KPIs ---------
    canal_mas_envios = resumen.order_by("-total_enviadas").first()
    canal_mas_fallos = resumen.order_by("-porcentaje_fallo").first()

    # --------- Tipos para el select ---------
    tipos = TipoNotificacion.objects.order_by("nombre_tipo").values("id", "nombre_tipo").distinct()

    context = {
        "resumen": resumen,
        "canal_mas_envios": canal_mas_envios,
        "canal_mas_fallos": canal_mas_fallos,
        "tipos": tipos,
        "f_fecha_inicio": fecha_inicio,
        "f_fecha_fin": fecha_fin,
        "f_canal": canal,
        "f_tipo": tipo_id,
        "f_estado_envio": estado_envio,
    }

    return render(request, "mensajes/reporte_canal.html", context)