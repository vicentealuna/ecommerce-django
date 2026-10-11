from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, render, redirect
from apps.orders.models import Orden
from apps.catalog.models import ItemStock
from .models import Despacho, MovimientoInventario
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction

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
    
# Aceptar solo POST y agrupar los cambios del despacho en una transacción.
@require_POST
@transaction.atomic   
 
def despachar(request, orden_id):
    """Recibe la solicitud de despacho; todavía no modifica inventario."""
    
     # Solicitar el bloqueo de la orden durante la transacción.
    orden = get_object_or_404(
        Orden.objects.select_for_update(),
        pk=orden_id,
    )
        # Rechazar las órdenes que ya no están pendientes de despacho.
    if orden.estado != Orden.Estado.READY_TO_SHIP:
        messages.error(request, 'Esta orden ya no está pendiente de despacho.')
        return redirect('warehouse:detalle', orden_id=orden.pk)
    
        # Obtener los artículos y sus existencias para comprobar el inventario.
    items = orden.items.select_related('variante__producto', 'variante__stock')
    
        # Impedir el despacho de una orden sin artículos.
    if not items:
        messages.error(request, 'No se puede despachar una orden sin artículos.')
        return redirect('warehouse:detalle', orden_id=orden.pk)
    
        # Revisar las existencias actuales de cada artículo.
    for item in items:
        stock = getattr(item.variante, 'stock', None)
        disponible = stock.cantidad if stock is not None else 0
        
                # Detener la solicitud si este artículo no tiene suficientes existencias.
        if item.cantidad > disponible:
            messages.error(
                request,
                f'Inventario insuficiente para {item.variante.producto.nombre} '
                f'({item.variante.nombre}): se necesitan {item.cantidad} '
                f'y hay {disponible}.',
            )
            return redirect('warehouse:detalle', orden_id=orden.pk)
        
    # Volver al detalle mientras construimos la lógica del despacho.
    return redirect('warehouse:detalle', orden_id=orden.pk)

