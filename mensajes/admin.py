# admin.py
from django.contrib import admin
from mensajes.models import Pago, Notificacion, PerfilAlumno, TipoNotificacion
from django.utils import timezone

@admin.register(PerfilAlumno)
class AlumnoAdmin(admin.ModelAdmin):
    # Campos que se muestran en la lista de registros
    list_display = ('user', 'dni', 'telefono', 'estado_pago', 'estado_documentacion', 'carrera')
    
    # Campos que se pueden editar en el formulario del registro
    fields = ('user', 'dni', 'telefono', 'estado_pago', 'estado_documentacion', 'carrera')
    
    # Opcional: agregar filtros rápidos en la barra lateral
    list_filter = ('estado_pago', 'estado_documentacion', 'carrera')
    
    # Opcional: agregar barra de búsqueda por nombre, apellido o DNI
    search_fields = ('user__first_name', 'user__last_name', 'dni')
