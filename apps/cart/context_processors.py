from apps.cart.carrito import contar_articulos


def carrito_context(request):
    return {'carrito_cantidad': contar_articulos(request.session)}
