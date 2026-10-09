from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

from apps.promotions.models import Cupon


@dataclass(frozen=True)
class ResultadoCupon:
    valido: bool
    descuento: Decimal
    motivo: str
    cupon: Cupon | None = None


def validar_cupon(codigo, subtotal):
    codigo_normalizado = (codigo or '').strip()
    try:
        subtotal_decimal = Decimal(str(subtotal))
    except (TypeError, ValueError):
        subtotal_decimal = Decimal('0')
    if subtotal_decimal < 0:
        subtotal_decimal = Decimal('0')

    cupon = Cupon.objects.filter(codigo__iexact=codigo_normalizado).first()
    if cupon is None:
        return ResultadoCupon(False, Decimal('0'), 'El cupón no existe.')
    if not cupon.activo:
        return ResultadoCupon(False, Decimal('0'), 'El cupón está inactivo.', cupon)

    ahora = timezone.now()
    if ahora < cupon.valido_desde:
        return ResultadoCupon(False, Decimal('0'), 'El cupón todavía no está vigente.', cupon)
    if ahora > cupon.valido_hasta:
        return ResultadoCupon(False, Decimal('0'), 'El cupón venció.', cupon)
    if subtotal_decimal < cupon.total_minimo:
        minimo = f'{cupon.total_minimo:.2f}'
        return ResultadoCupon(
            False,
            Decimal('0'),
            f'La compra mínima para este cupón es de ${minimo}.',
            cupon,
        )

    if cupon.tipo_descuento == Cupon.TipoDescuento.PORCENTAJE:
        descuento = (subtotal_decimal * cupon.monto / Decimal('100')).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP,
        )
    else:
        descuento = cupon.monto

    descuento = min(descuento, subtotal_decimal)
    return ResultadoCupon(True, descuento, '', cupon)

# Create your views here.
