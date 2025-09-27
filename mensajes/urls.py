from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('filtrar_alumnos/', views.filtrar_alumnos, name='filtrar_alumnos'),
    path('formulario/', views.formulario_alumno, name='formulario_email'),
    path('detalle/', views.detalle_alumno, name='detalle_alumno'),
    path('mensaje/', views.formulario_email, name='envio'),
]
