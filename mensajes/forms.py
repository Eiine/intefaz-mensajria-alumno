# mensajes/forms.py
from django import forms
from .models import PerfilAlumno, Notificacion, Carrera, Pago, MensajeInterno

class PerfilAlumnoForm(forms.ModelForm):
    class Meta:
        model = PerfilAlumno
        fields = '__all__'

class NotificacionForm(forms.ModelForm):
    class Meta:
        model = Notificacion
        fields = '__all__'

class CarreraForm(forms.ModelForm):
    class Meta:
        model = Carrera
        fields = '__all__'

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = '__all__'

class MensajeInternoForm(forms.ModelForm):
    class Meta:
        model = MensajeInterno
        fields = '__all__'
