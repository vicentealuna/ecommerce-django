from django.db.models import Sum
from django.shortcuts import get_object_or_404, render

from apps.orders.models import Orden


def lista(request):
    """Muestra las órdenes pendientes de despacho."""

    # Obtener únicamente las órdenes listas para despachar.
    ordenes = Orden.objects.filter(estado=Orden.Estado.READY_TO_SHIP)

    # Sumar las cantidades de los artículos de cada orden.
    ordenes = ordenes.annotate(cantidad_articulos=Sum('items__cantidad', default=0))

    # Atender primero las órdenes más antiguas.
    ordenes = ordenes.order_by('fecha_creacion')

    # Entregar las órdenes a la plantilla del almacén.
    return render(request, 'warehouse/lista.html', {'ordenes': ordenes})

def detalle(request, orden_id):
    """Muestra los detalles de una orden específica."""

    # Buscar la orden o responder con 404 si no existe.
    orden = get_object_or_404(Orden, id=orden_id)

    # Obtener los artículos con su variante, producto e inventario en una consulta.
    items = orden.items.select_related('variante__producto', 'variante__stock')

    # Entregar los datos de envío y los artículos a la plantilla de detalle.
    return render(request, 'warehouse/detalle.html', {
        'orden': orden,
        'items': items,
    })
