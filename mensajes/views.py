
from django.shortcuts import render

def inicio(request):
    # Acá Django buscará un template llamado 'inicio.html' en tu carpeta templates
    return render(request, 'inicio.html')

