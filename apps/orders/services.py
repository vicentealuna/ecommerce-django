from decimal import Decimal

from django.db import transaction

from apps.cart.carrito import obtener_resumen
from apps.catalog.models import ItemStock, Producto, Variante
from apps.orders.models import ItemOrden, Orden
from apps.promotions.cupones import validar_cupon


class ErrorCheckout(ValueError):
    pass


def validar_productos_carrito_activos(session):
    carrito = session.get('carrito', {})
    if not isinstance(carrito, dict):
        raise ErrorCheckout(
            'El carrito contiene un producto que ya no está disponible. '
            'Revísalo antes de continuar.'
        )

    variantes_ids = set()
    for variante_id, cantidad in carrito.items():
        try:
            cantidad = int(cantidad)
            variante_id = int(variante_id)
        except (TypeError, ValueError):
            raise ErrorCheckout(
                'El carrito contiene un producto que ya no está disponible. '
                'Revísalo antes de continuar.'
            ) from None

        if cantidad > 0:
            variantes_ids.add(variante_id)

    if not variantes_ids:
        return variantes_ids

    variantes = {
        variante.pk: variante
        for variante in Variante.objects.filter(pk__in=variantes_ids)
    }
    if len(variantes) != len(variantes_ids):
        raise ErrorCheckout(
            'Un producto del carrito ya no está disponible. '
            'Revisa el carrito antes de continuar.'
        )

    productos_ids = {variante.producto_id for variante in variantes.values()}
    productos = Producto.objects.filter(pk__in=productos_ids)
    if productos.filter(activo=False).exists():
        raise ErrorCheckout(
            'Un producto del carrito ya no está disponible. '
            'Revisa el carrito antes de continuar.'
        )
    return variantes_ids


def crear_orden_desde_carrito(session, datos_envio):
    with transaction.atomic():
        variantes_carrito_ids = validar_productos_carrito_activos(session)
        lineas, _ = obtener_resumen(session)
        if not lineas:
            raise ErrorCheckout('El carrito está vacío.')

        variantes_ids = [linea['variante'].pk for linea in lineas]
        if set(variantes_ids) != variantes_carrito_ids:
            raise ErrorCheckout(
                'Un producto del carrito ya no está disponible. '
                'Revisa el carrito antes de continuar.'
            )
        cantidades = {linea['variante'].pk: linea['cantidad'] for linea in lineas}

        variantes = {
            variante.pk: variante
            for variante in Variante.objects.select_for_update()
            .select_related('producto')
            .filter(pk__in=variantes_ids)
        }
        lineas_actualizadas = []
        subtotal = Decimal('0')

        for variante_id in variantes_ids:
            variante = variantes.get(variante_id)
            if variante is None or not variante.producto.activo:
                raise ErrorCheckout(
                    'Un producto del carrito ya no está disponible. '
                    'Revisa el carrito antes de continuar.'
                )

            cantidad = cantidades[variante_id]
            stock = (
                ItemStock.objects.select_for_update()
                .filter(variante_id=variante_id)
                .first()
            )
            disponible = stock.cantidad if stock else 0
            if cantidad > disponible:
                raise ErrorCheckout(
                    f'Inventario insuficiente para {variante.producto.nombre}. '
                    f'Solicitaste {cantidad} y quedan {disponible}.'
                )

            precio_unitario = variante.producto.precio_final
            total_linea = precio_unitario * cantidad
            subtotal += total_linea
            lineas_actualizadas.append({
                'variante': variante,
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'total_linea': total_linea,
            })

        codigo = session.get('cupon_codigo')
        descuento = Decimal('0')
        cupon = None
        if codigo:
            resultado = validar_cupon(codigo, subtotal)
            if not resultado.valido:
                raise ErrorCheckout(resultado.motivo)
            descuento = resultado.descuento
            cupon = resultado.cupon

        if not session.session_key:
            session.create()

        orden = Orden.objects.create(
            clave_sesion=session.session_key,
            nombre_envio=datos_envio['nombre_envio'],
            direccion_envio=datos_envio['direccion_envio'],
            telefono=datos_envio['telefono'],
            estado=Orden.Estado.READY_TO_SHIP,
            subtotal=subtotal,
            descuento=descuento,
            total=subtotal - descuento,
            cupon=cupon,
        )
        ItemOrden.objects.bulk_create([
            ItemOrden(
                orden=orden,
                variante=linea['variante'],
                cantidad=linea['cantidad'],
                precio_unitario=linea['precio_unitario'],
                total_linea=linea['total_linea'],
            )
            for linea in lineas_actualizadas
        ])

    session.pop('carrito', None)
    session.pop('cupon_codigo', None)
    session.modified = True
    return orden
