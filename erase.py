import os
import django
from django.db import connection

# 1. Configuración de Entorno Django
# Asegúrate de que 'interfas_mensajria.settings' sea el nombre de tu archivo settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interfas_mensajria.settings')
django.setup()

# Lista de todas las tablas de tu aplicación y la tabla de historial de Django
# Las nombramos exactamente como aparecen en PostgreSQL (mensajes_modelo)
TABLAS_A_ELIMINAR = [
    "mensajes_carrera",
    "mensajes_pago",
    "mensajes_tiponotificacion",
    "mensajes_plantilla",
    "mensajes_usuario",
    "mensajes_alumno",
    "mensajes_notificacion",
    "mensajes_preferenciasnotificaciones",
    "django_migrations",  # Fundamental para resetear el historial
]

def drop_all_app_tables():
    """
    Ejecuta el comando DROP TABLE IF EXISTS para todas las tablas especificadas.
    """
    
    # 1. Formar la consulta SQL
    # Unir la lista de tablas con comas.
    tables_list_sql = ", ".join(TABLAS_A_ELIMINAR)
    
    # Construir la consulta completa con CASCADE para manejar las dependencias
    sql_command = f"""
    DROP TABLE IF EXISTS
        {tables_list_sql}
    CASCADE;
    """
    
    # 2. Ejecutar la consulta SQL usando la conexión de Django
    with connection.cursor() as cursor:
        try:
            print("-------------------------------------------------------")
            print(f"🔄 Intentando eliminar las tablas de la aplicación 'mensajes'...")
            
            # Ejecutar el comando
            cursor.execute(sql_command)
            
            print("✅ LIMPIEZA EXITOSA.")
            print("Las tablas y el historial de migración han sido eliminados de la BD.")
            print("-------------------------------------------------------")
            
        except Exception as e:
            print(f"❌ ERROR durante la eliminación de tablas: {e}")
            print("Asegúrate de que el servidor de PostgreSQL esté corriendo y la configuración de DB en settings.py sea correcta.")
            print("-------------------------------------------------------")

if __name__ == "__main__":
    drop_all_app_tables()