from django.core.validators import MinValueValidator
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    padre = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='subcategorias',
    )

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['nombre']

    def __str__(self):
        if self.padre:
            return f'{self.padre.nombre} > {self.nombre}'
        return self.nombre


class Producto(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos',
    )
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    # Si tiene valor, el producto está en oferta y este es el precio que se cobra.
    precio_oferta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    destacado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.nombre

    @property
    def en_oferta(self):
        return self.precio_oferta is not None

    @property
    def precio_final(self):
        """Precio que se cobra: el de oferta si existe; si no, el normal."""
        if self.en_oferta:
            return self.precio_oferta
        return self.precio


class ImagenProducto(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='imagenes',
    )
    imagen = models.ImageField(upload_to='productos/')
    texto_alternativo = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'imagen de producto'
        verbose_name_plural = 'imágenes de producto'
        ordering = ['id']

    def __str__(self):
        return f'Imagen de {self.producto.nombre}'


class Variante(models.Model):
    """
    Lo que realmente se vende: una talla o color de un producto.
    Todo producto tiene al menos una. Si no tiene tallas ni colores,
    tiene una sola variante llamada "Única".
    """
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='variantes',
    )
    nombre = models.CharField(max_length=80, default='Única')

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['producto', 'nombre'],
                name='variante_unica_por_producto',
            ),
        ]

    def __str__(self):
        return f'{self.producto.nombre} ({self.nombre})'

    @property
    def cantidad_disponible(self):
        """Unidades en inventario. Devuelve 0 si la variante aún no tiene ItemStock."""
        try:
            return self.stock.cantidad
        except ItemStock.DoesNotExist:
            return 0


class ItemStock(models.Model):
    variante = models.OneToOneField(
        Variante,
        on_delete=models.CASCADE,
        related_name='stock',
    )
    cantidad = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'inventario'
        verbose_name_plural = 'inventario'

    def __str__(self):
        return f'{self.variante}: {self.cantidad}'
