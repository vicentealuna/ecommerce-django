from django.contrib import messages
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.models import ItemStock
from apps.orders.models import Orden

from .models import Despacho, MovimientoInventario


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
    orden = get_object_or_404(Orden, pk=orden_id)

    # Obtener los artículos con su variante, producto e inventario en una consulta.
    items = orden.items.select_related('variante__producto', 'variante__stock')

    # Entregar los datos de envío y los artículos a la plantilla de detalle.
    return render(request, 'warehouse/detalle.html', {
        'orden': orden,
        'items': items,
        'pendiente_despacho': orden.estado == Orden.Estado.READY_TO_SHIP,
    })


# Aceptar solo POST y agrupar los cambios del despacho en una transacción.
@require_POST
@transaction.atomic
def despachar(request, orden_id):
    """Valida y registra el despacho completo dentro de una transacción."""

    # Solicitar el bloqueo de la orden en bases de datos que lo admiten.
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

    # Revisar todos los artículos antes de modificar el inventario.
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

    # Cambiar el estado solo si la orden sigue pendiente en la base de datos.
    actualizadas = Orden.objects.filter(
        pk=orden.pk,
        estado=Orden.Estado.READY_TO_SHIP,
    ).update(estado=Orden.Estado.DESPATCHED)

    if actualizadas != 1:
        messages.error(request, 'Esta orden ya no está pendiente de despacho.')
        return redirect('warehouse:detalle', orden_id=orden.pk)

    # Descontar cada artículo solo si todavía alcanza el inventario.
    for item in items:
        descontados = ItemStock.objects.filter(
            variante_id=item.variante_id,
            cantidad__gte=item.cantidad,
        ).update(cantidad=F('cantidad') - item.cantidad)

        if descontados != 1:
            # Deshacer también los descuentos anteriores y el cambio de estado.
            transaction.set_rollback(True)
            messages.error(
                request,
                f'Inventario insuficiente para {item.variante.producto.nombre} '
                f'({item.variante.nombre}). No se despachó ningún artículo.',
            )
            return redirect('warehouse:detalle', orden_id=orden.pk)

        # Registrar la salida de inventario asociada a esta orden.
        MovimientoInventario.objects.create(
            variante=item.variante,
            tipo=MovimientoInventario.Tipo.SALIDA,
            cantidad=item.cantidad,
            motivo=f'Despacho de la orden #{orden.pk}',
            orden_relacionada=orden,
        )

    # Registrar el despacho después de descontar todos los artículos.
    Despacho.objects.create(orden=orden)

    # Informar del resultado y regresar a las órdenes pendientes.
    messages.success(request, f'Orden #{orden.pk} despachada correctamente.')
    return redirect('warehouse:lista')
