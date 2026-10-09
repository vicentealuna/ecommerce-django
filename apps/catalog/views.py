from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import Categoria, Producto


def inicio(request):
    """Muestra categorías, productos destacados y ofertas."""

    # Obtener los productos activos de cada sección.
    destacados = Producto.objects.filter(activo=True, destacado=True)
    ofertas = Producto.objects.filter(
        activo=True,
        precio_oferta__isnull=False,
    )

    # Obtener las categorías para el menú.
    categorias = Categoria.objects.all()

    # Entregar los datos a la página de inicio.
    return render(request, 'catalog/inicio.html', {
        'destacados': destacados,
        'ofertas': ofertas,
        'categorias': categorias,
    })


def categoria(request, slug):
    """Muestra productos de una categoría y sus subcategorías directas."""

    # Buscar la categoría o responder con 404 si no existe.
    categoria_actual = get_object_or_404(Categoria, slug=slug)

    # Seleccionar productos activos de la categoría o de sus hijas.
    productos = Producto.objects.filter(
        Q(categoria=categoria_actual)
        | Q(categoria__padre=categoria_actual),
        activo=True,
    )

    # Entregar los datos a la página de categoría.
    return render(request, 'catalog/categoria.html', {
        'categoria_actual': categoria_actual,
        'productos': productos,
    })