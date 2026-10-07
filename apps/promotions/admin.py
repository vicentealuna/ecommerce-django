from django.contrib import admin

from .models import Cupon


@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'tipo_descuento', 'monto', 'total_minimo',
        'valido_desde', 'valido_hasta', 'activo',
    ]
    list_editable = ['activo']
    list_filter = ['tipo_descuento', 'activo']
    search_fields = ['codigo']
