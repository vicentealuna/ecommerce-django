from django.urls import path

from . import views

# Identificar estas rutas al usar la etiqueta url en las plantillas.
app_name = 'warehouse'

urlpatterns = [
    # Mostrar la lista de órdenes pendientes.
    path('', views.lista, name='lista'),
    # Consultar una orden usando el identificador recibido en la URL.
    path('orden/<int:orden_id>/', views.detalle, name='detalle'),
    # Enviar la solicitud de despacho a la vista que acepta solo POST.
    path('orden/<int:orden_id>/despachar/', views.despachar, name='despachar'),
]
