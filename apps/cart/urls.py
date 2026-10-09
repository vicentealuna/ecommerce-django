from django.urls import path

from apps.cart.views import (
    agregar_al_carrito,
    aplicar_cupon,
    actualizar_carrito,
    eliminar_del_carrito,
    quitar_cupon,
    ver_carrito,
)

app_name = 'cart'

urlpatterns = [
    path('', ver_carrito, name='ver'),
    path('agregar/', agregar_al_carrito, name='agregar'),
    path('actualizar/', actualizar_carrito, name='actualizar'),
    path('eliminar/', eliminar_del_carrito, name='eliminar'),
    path('cupon/', aplicar_cupon, name='aplicar_cupon'),
    path('cupon/quitar/', quitar_cupon, name='quitar_cupon'),
]
