from django.urls import path

from apps.cart.views import (
    agregar_al_carrito,
    actualizar_carrito,
    eliminar_del_carrito,
    ver_carrito,
)
from config.views import en_construccion

app_name = 'cart'

urlpatterns = [
    path('', ver_carrito, name='ver'),
    path('agregar/', agregar_al_carrito, name='agregar'),
    path('actualizar/', actualizar_carrito, name='actualizar'),
    path('eliminar/', eliminar_del_carrito, name='eliminar'),
    path('cupon/', en_construccion, name='aplicar_cupon'),
    path('cupon/quitar/', en_construccion, name='quitar_cupon'),
]
