from django.urls import path

from config.views import en_construccion

from . import views

app_name = 'warehouse'

# Mostrar las órdenes pendientes en la página principal del almacén.
urlpatterns = [
    path('', views.lista, name='lista'),
    path('orden/<int:orden_id>/', en_construccion, name='detalle'),
    path('orden/<int:orden_id>/despachar/', en_construccion, name='despachar'),
]


