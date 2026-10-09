from django.shortcuts import render

from .models import Producto


def inicio(request):
    """Muestra los productos activos destacados y en oferta."""

    # Obtener los dos grupos de productos del inicio.
    destacados = Producto.objects.filter(activo=True, destacado=True)
    ofertas = Producto.objects.filter(activo=True, precio_oferta__isnull=False)

    # Entregar los productos a la plantilla.
    return render(request, 'catalog/inicio.html', {
        'destacados': destacados,
        'ofertas': ofertas,
    })
