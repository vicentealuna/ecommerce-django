from django.urls import path

from config.views import en_construccion

app_name = 'cart'

urlpatterns = [
    path('', en_construccion, name='ver'),
    path('agregar/', en_construccion, name='agregar'),
    path('actualizar/', en_construccion, name='actualizar'),
    path('eliminar/', en_construccion, name='eliminar'),
    path('cupon/', en_construccion, name='aplicar_cupon'),
    path('cupon/quitar/', en_construccion, name='quitar_cupon'),
]
