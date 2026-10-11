from django.urls import path

from config.views import en_construccion

from . import views

# Identificar estas rutas al usar la etiqueta url en las plantillas.
app_name = 'warehouse'

urlpatterns = [
    # Mostrar la lista de órdenes pendientes.
    path('', views.lista, name='lista'),
    # Consultar una orden usando el identificador recibido en la URL.
    path('orden/<int:orden_id>/', views.detalle, name='detalle'),
    # Reservar la ruta del despacho hasta implementar su lógica.
    path('orden/<int:orden_id>/despachar/', en_construccion, name='despachar'),
]
