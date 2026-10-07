from django.core.validators import MinValueValidator
from django.db import models


class Cupon(models.Model):
    class TipoDescuento(models.TextChoices):
        PORCENTAJE = 'PORCENTAJE', 'Porcentaje'
        FIJO = 'FIJO', 'Monto fijo'

    codigo = models.CharField(max_length=30, unique=True)
    tipo_descuento = models.CharField(max_length=12, choices=TipoDescuento.choices)
    # Si el tipo es PORCENTAJE, monto es el porcentaje (10 = 10 %). Si es FIJO, es dinero.
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    activo = models.BooleanField(default=True)
    valido_desde = models.DateTimeField()
    valido_hasta = models.DateTimeField()
    total_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = 'cupón'
        verbose_name_plural = 'cupones'
        ordering = ['codigo']

    def __str__(self):
        return self.codigo

    def save(self, *args, **kwargs):
        # El código se guarda siempre en mayúsculas y sin espacios alrededor.
        self.codigo = self.codigo.strip().upper()
        super().save(*args, **kwargs)
