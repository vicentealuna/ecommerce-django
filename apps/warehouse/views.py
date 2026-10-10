from django.shortcuts import render

from apps.orders.models import Orden

# Create your views here.

def lista(request):
    """Muestra las órdenes pendientes de despacho."""
        # Obtener únicamente las órdenes listas para despachar.
    ordenes = Orden.objects.filter(estado=Orden.Estado.READY_TO_SHIP)
        # Atender primero las órdenes más antiguas.
    ordenes = ordenes.order_by('fecha_creacion')
        # Entregar las órdenes a la plantilla del almacén.
    return render(request, 'warehouse/lista.html',{'ordenes' : ordenes,})
   