from django.shortcuts import render

from .models import Producto

def inicio(request):
    destacados = Producto.objects.filter(activo=True, destacado=True)
    ofertas = Producto.objects.filter(activo=True, precio_oferta__isnull=False)

    return render(request, 'catalog/inicio.html', {
        'destacados': destacados,
        'ofertas': ofertas,
    })