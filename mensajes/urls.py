from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
urlpatterns = [

    #Login
    path('', views.login_view, name='login'),
    path("logout/", views.logout_view, name="logout"),
    path('home/',views.listar_alumnos, name='alumnos_lista'),
    path('panel/', views.panel_admin, name='panel_admin'),
    path('config/', views.config, name='configuraciones'),
    path('ajax/notificaciones/<int:alumno_id>/', views.get_notificaciones, name='ajax_notificaciones'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
    path('notificaciones/crear/', views.crear_notificacion, name='notificaciones_crear'),
     # CRUD PerfilAlumno
    path('alumnos/', views.alumnos_lista, name='listar_alumnos'),
    path('filtrar_alumnos/', views.filtrar_alumnos, name='filtrar_alumnos'),
    path('alumnos/crear/', views.interfaz, name='perfil_alumno_crear'),
    path('alumnos/<int:pk>/editar/', views.interfaz, name='perfil_alumno_editar'),
    path('alumnos/<int:pk>/eliminar/', views.interfaz, name='perfil_alumno_eliminar'),
    path('alumnos/<int:pk>/', views.interfaz, name='perfil_alumno_detalle'),
    path("mensajes/", views.mensajes_view, name="mensajes"),
    path('api/mensajes/nuevos/', views.mensajes_nuevos, name='mensajes_nuevos'),
    path('api/mensajes/enviar/', views.enviar_mensaje, name='enviar_mensaje'),
    path("api/mensajes/", views.obtener_mensajes, name="obtener_mensajes_usuario"),
    path('api/actualizar-preferencia/', views.actualizar_preferencia, name='actualizar_preferencia'),
    path('api/mensajes/marcar_leidos/', views.marcar_leidos, name='marcar_leidos'),
    path("circular/", views.circular, name="circular"),
    # CRUD Notificacion

    path('notificaciones/crear/', views.crear_notificacion, name='crear_notificacion'),
    
    #debug data
     path('panelgeneral/', views.panel_general, name='panel_general'),
]
