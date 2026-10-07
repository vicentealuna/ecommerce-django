from django.contrib import admin

from .models import Despacho, MovimientoInventario


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ['fecha_creacion', 'variante', 'tipo', 'cantidad', 'motivo', 'orden_relacionada']
    list_filter = ['tipo']
    search_fields = ['variante__producto__nombre', 'motivo']


@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ['orden', 'fecha_despacho']
