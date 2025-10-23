from django.urls import path
from . import views

urlpatterns = [

    path('', views.listar_alumnos, name='alumnos_lista'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
     # CRUD PerfilAlumno
    path('alumnos/', views.interfaz, name='alumnos_lista'),
    path('filtrar_alumnos/', views.filtrar_alumnos, name='filtrar_alumnos'),
    path('alumnos/crear/', views.interfaz, name='perfil_alumno_crear'),
    path('alumnos/<int:pk>/editar/', views.interfaz, name='perfil_alumno_editar'),
    path('alumnos/<int:pk>/eliminar/', views.interfaz, name='perfil_alumno_eliminar'),
    path('alumnos/<int:pk>/', views.interfaz, name='perfil_alumno_detalle'),

    # CRUD Notificacion
    path('notificaciones/', views.listar_notificaciones, name='listar_notificaciones'),
    path('notificaciones/crear/', views.crear_notificacion, name='crear_notificacion'),
    path('notificaciones/editar/<int:pk>/', views.editar_notificacion, name='editar_notificacion'),
    path('notificaciones/eliminar/<int:pk>/', views.eliminar_notificacion, name='eliminar_notificacion'),
]
