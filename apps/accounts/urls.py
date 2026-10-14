from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('ingresar/', views.ingresar, name='ingresar'),
    path('salir/', views.salir, name='salir'),
]
