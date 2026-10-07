from django.core.validators import MinValueValidator
from django.db import models


class Orden(models.Model):
    class Estado(models.TextChoices):
        READY_TO_SHIP = 'READY_TO_SHIP', 'Lista para despachar'
        DESPATCHED = 'DESPATCHED', 'Despachada'

    # Sesión del navegador que hizo la compra (no hay usuarios).
    clave_sesion = models.CharField(max_length=40)
    nombre_envio = models.CharField(max_length=150)
    direccion_envio = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.READY_TO_SHIP,
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cupon = models.ForeignKey(
        'promotions.Cupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'orden'
        verbose_name_plural = 'órdenes'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Orden #{self.pk} - {self.nombre_envio}'


class ItemOrden(models.Model):
    orden = models.ForeignKey(
        Orden,
        on_delete=models.CASCADE,
        related_name='items',
    )
    # PROTECT: no se puede borrar una variante que ya fue vendida.
    variante = models.ForeignKey(
        'catalog.Variante',
        on_delete=models.PROTECT,
        related_name='items_orden',
    )
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    # Copia del precio en el momento de la compra.
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total_linea = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'línea de orden'
        verbose_name_plural = 'líneas de orden'

    def __str__(self):
        return f'{self.cantidad} x {self.variante}'
