import re

from django import forms


class CheckoutForm(forms.Form):
    nombre_envio = forms.CharField(
        label='Nombre completo',
        max_length=150,
        widget=forms.TextInput(attrs={
            'autocomplete': 'name',
            'class': 'form-control',
            'required': True,
        }),
    )
    direccion_envio = forms.CharField(
        label='Dirección de envío',
        max_length=255,
        widget=forms.TextInput(attrs={
            'autocomplete': 'street-address',
            'class': 'form-control',
            'required': True,
        }),
    )
    telefono = forms.CharField(
        label='Teléfono',
        max_length=20,
        widget=forms.TextInput(attrs={
            'autocomplete': 'tel',
            'class': 'form-control',
            'required': True,
            'type': 'tel',
        }),
    )

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono'].strip()
        if not re.fullmatch(r'[0-9 -]+', telefono):
            raise forms.ValidationError(
                'Usa únicamente dígitos, espacios y guiones.'
            )

        digitos = sum(caracter.isdigit() for caracter in telefono)
        if not 7 <= digitos <= 15:
            raise forms.ValidationError(
                'El teléfono debe contener entre 7 y 15 dígitos.'
            )
        return telefono
