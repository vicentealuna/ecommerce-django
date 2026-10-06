from django.core.validators import MinValueValidator
from django.db import models


class MovimientoInventario(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = 'ENTRADA', 'Entrada'
        SALIDA = 'SALIDA', 'Salida'

    variante = models.ForeignKey(
        'catalog.Variante',
        on_delete=models.PROTECT,
        related_name='movimientos',
    )
    tipo = models.CharField(max_length=8, choices=Tipo.choices)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    motivo = models.CharField(max_length=200)
    orden_relacionada = models.ForeignKey(
        'orders.Orden',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='movimientos',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'movimiento de inventario'
        verbose_name_plural = 'movimientos de inventario'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.tipo} {self.cantidad} - {self.variante}'


class Despacho(models.Model):
    # OneToOne: una orden solo se puede despachar una vez.
    orden = models.OneToOneField(
        'orders.Orden',
        on_delete=models.PROTECT,
        related_name='despacho',
    )
    fecha_despacho = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_despacho']

    def __str__(self):
        return f'Despacho de la orden #{self.orden_id}'
