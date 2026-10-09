from decimal import Decimal

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.cart.carrito import (
    ErrorCarrito,
    agregar_variante,
    actualizar_variante,
    eliminar_variante,
    obtener_resumen,
)
from apps.promotions.cupones import validar_cupon


def _obtener_datos_cupon(request, subtotal):
    codigo = request.session.get('cupon_codigo')
    if not codigo:
        return Decimal('0'), subtotal, None

    resultado = validar_cupon(codigo, subtotal)
    if not resultado.valido:
        request.session.pop('cupon_codigo', None)
        messages.error(request, resultado.motivo)
        return Decimal('0'), subtotal, None

    return resultado.descuento, subtotal - resultado.descuento, resultado.cupon


def ver_carrito(request):
    lineas, subtotal = obtener_resumen(request.session)
    descuento, total, cupon = _obtener_datos_cupon(request, subtotal)
    return render(request, 'cart/carrito.html', {
        'lineas': lineas,
        'subtotal': subtotal,
        'descuento': descuento,
        'total': total,
        'cupon': cupon,
        'carrito_vacio': not lineas,
    })


@require_POST
def agregar_al_carrito(request):
    try:
        producto = agregar_variante(
            request.session,
            request.POST.get('variante_id'),
            request.POST.get('cantidad'),
        )
    except ErrorCarrito as error:
        messages.error(request, str(error))
    else:
        messages.success(request, f'{producto} agregado al carrito.')
    return redirect('cart:ver')


@require_POST
def actualizar_carrito(request):
    try:
        actualizado = actualizar_variante(
            request.session,
            request.POST.get('variante_id'),
            request.POST.get('cantidad'),
        )
    except ErrorCarrito as error:
        messages.error(request, str(error))
    else:
        if actualizado:
            messages.success(request, 'El carrito se actualizó correctamente.')
        else:
            messages.success(request, 'La línea del carrito fue eliminada.')
    return redirect('cart:ver')


@require_POST
def eliminar_del_carrito(request):
    try:
        eliminar_variante(request.session, request.POST.get('variante_id'))
    except ErrorCarrito as error:
        messages.error(request, str(error))
    else:
        messages.success(request, 'Producto eliminado del carrito.')
    return redirect('cart:ver')


@require_POST
def aplicar_cupon(request):
    codigo = request.POST.get('codigo', '')
    _, subtotal = obtener_resumen(request.session)
    resultado = validar_cupon(codigo, subtotal)
    if not resultado.valido:
        messages.error(request, resultado.motivo)
    else:
        request.session['cupon_codigo'] = resultado.cupon.codigo
        request.session.modified = True
        messages.success(request, 'Cupón aplicado correctamente.')
    return redirect('cart:ver')


@require_POST
def quitar_cupon(request):
    request.session.pop('cupon_codigo', None)
    request.session.modified = True
    messages.success(request, 'Cupón eliminado.')
    return redirect('cart:ver')
