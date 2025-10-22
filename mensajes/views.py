from django.shortcuts import render
from .models import Alumno 
from django.http import JsonResponse


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