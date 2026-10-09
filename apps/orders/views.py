from decimal import Decimal

from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.cart.carrito import obtener_resumen
from apps.orders.forms import CheckoutForm
from apps.orders.models import Orden
from apps.orders.services import ErrorCheckout, crear_orden_desde_carrito
from apps.promotions.cupones import validar_cupon


def _resumen_checkout(request):
    lineas, subtotal = obtener_resumen(request.session)
    codigo = request.session.get('cupon_codigo')
    descuento = Decimal('0')
    cupon = None

    if codigo:
        if not lineas:
            request.session.pop('cupon_codigo', None)
            request.session.modified = True
            return lineas, subtotal, descuento, subtotal, None, (
                'No puedes aplicar un cupón con el carrito vacío.'
            )

        resultado = validar_cupon(codigo, subtotal)
        if not resultado.valido:
            request.session.pop('cupon_codigo', None)
            request.session.modified = True
            return lineas, subtotal, descuento, subtotal, None, resultado.motivo
        descuento = resultado.descuento
        cupon = resultado.cupon

    return lineas, subtotal, descuento, subtotal - descuento, cupon, None


@require_http_methods(['GET', 'POST'])
def checkout(request):
    lineas, subtotal, descuento, total, cupon, error_cupon = _resumen_checkout(request)
    if not lineas:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('catalog:inicio')
    if error_cupon:
        messages.error(request, error_cupon)
        return redirect('cart:ver')

    if request.method == 'POST':
        formulario = CheckoutForm(request.POST)
        if formulario.is_valid():
            try:
                orden = crear_orden_desde_carrito(
                    request.session,
                    formulario.cleaned_data,
                )
            except ErrorCheckout as error:
                messages.error(request, str(error))
                return redirect('cart:ver')
            messages.success(request, 'Tu compra se confirmó correctamente.')
            return redirect('orders:confirmacion', orden_id=orden.pk)
    else:
        formulario = CheckoutForm()

    return render(request, 'orders/checkout.html', {
        'formulario': formulario,
        'lineas': lineas,
        'subtotal': subtotal,
        'descuento': descuento,
        'total': total,
        'cupon': cupon,
    })


def confirmacion(request, orden_id):
    clave_sesion = request.session.session_key
    if not clave_sesion:
        raise Http404
    orden = get_object_or_404(
        Orden.objects.prefetch_related('items__variante__producto'),
        pk=orden_id,
        clave_sesion=clave_sesion,
    )
    return render(request, 'orders/confirmacion.html', {'orden': orden})
