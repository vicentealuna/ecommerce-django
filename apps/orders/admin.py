from django.contrib import admin

from .models import ItemOrden, Orden


class ItemOrdenInline(admin.TabularInline):
    model = ItemOrden
    extra = 0


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_envio', 'estado', 'subtotal', 'descuento', 'total', 'fecha_creacion']
    list_filter = ['estado']
    search_fields = ['nombre_envio', 'telefono']
    inlines = [ItemOrdenInline]
