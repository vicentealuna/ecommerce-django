from django.contrib import admin
from django.utils.html import format_html

from .models import Categoria, ImagenProducto, ItemStock, Producto, Variante


def miniatura(imagen, alto):
    """Devuelve la etiqueta de una imagen pequeña, o un guion si aún no hay archivo."""
    if not imagen:
        return '—'
    return format_html(
        '<img src="{}" alt="" style="height: {}px; border-radius: 6px;">',
        imagen.url,
        alto,
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'padre', 'slug']
    prepopulated_fields = {'slug': ['nombre']}
    search_fields = ['nombre']


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    # Al lado de cada archivo se ve la imagen que ya está guardada.
    readonly_fields = ['vista_previa']

    @admin.display(description='Vista previa')
    def vista_previa(self, obj):
        return miniatura(obj.imagen if obj.pk else None, 80)


class VarianteInline(admin.TabularInline):
    model = Variante
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['imagen_principal', 'nombre', 'categoria', 'precio', 'precio_oferta', 'destacado', 'activo']
    list_display_links = ['imagen_principal', 'nombre']
    list_editable = ['destacado', 'activo']
    list_filter = ['categoria', 'destacado', 'activo']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ['nombre']}
    # Imágenes y variantes se editan en la misma pantalla del producto.
    inlines = [ImagenProductoInline, VarianteInline]

    @admin.display(description='Imagen')
    def imagen_principal(self, obj):
        primera = obj.imagenes.first()
        return miniatura(primera.imagen if primera else None, 48)


@admin.register(Variante)
class VarianteAdmin(admin.ModelAdmin):
    list_display = ['producto', 'nombre', 'cantidad_disponible']
    search_fields = ['producto__nombre', 'nombre']


@admin.register(ItemStock)
class ItemStockAdmin(admin.ModelAdmin):
    list_display = ['variante', 'cantidad']
    list_editable = ['cantidad']
    search_fields = ['variante__producto__nombre', 'variante__nombre']
