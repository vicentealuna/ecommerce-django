from django.shortcuts import render

from .models import Producto


def inicio(request):
    destacados = Producto.objects.filter(activo=True, destacado=True)
    return render(request, 'catalog/inicio.html', {'destacados': destacados})
