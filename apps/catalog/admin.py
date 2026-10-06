from django.contrib import admin

from .models import Categoria, ImagenProducto, ItemStock, Producto, Variante


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'padre', 'slug']
    prepopulated_fields = {'slug': ['nombre']}
    search_fields = ['nombre']


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1


class VarianteInline(admin.TabularInline):
    model = Variante
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'precio_oferta', 'destacado', 'activo']
    list_editable = ['destacado', 'activo']
    list_filter = ['categoria', 'destacado', 'activo']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ['nombre']}
    # Imágenes y variantes se editan en la misma pantalla del producto.
    inlines = [ImagenProductoInline, VarianteInline]


@admin.register(Variante)
class VarianteAdmin(admin.ModelAdmin):
    list_display = ['producto', 'nombre', 'cantidad_disponible']
    search_fields = ['producto__nombre', 'nombre']


@admin.register(ItemStock)
class ItemStockAdmin(admin.ModelAdmin):
    list_display = ['variante', 'cantidad']
    list_editable = ['cantidad']
    search_fields = ['variante__producto__nombre', 'variante__nombre']
