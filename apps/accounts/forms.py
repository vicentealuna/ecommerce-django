from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class RegistroForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dar a todos los campos el mismo estilo que el resto de formularios.
        for campo in self.fields.values():
            campo.widget.attrs['class'] = 'form-control'
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['email'].widget.attrs['autocomplete'] = 'email'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese correo.')
        return email


class IngresoForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs['class'] = 'form-control'
        self.fields['username'].label = 'Nombre de usuario'
