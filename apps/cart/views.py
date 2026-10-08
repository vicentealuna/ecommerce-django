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


def ver_carrito(request):
    lineas, subtotal = obtener_resumen(request.session)
    return render(request, 'cart/carrito.html', {
        'lineas': lineas,
        'subtotal': subtotal,
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
