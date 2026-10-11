from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.promotions.models import Cupon
from apps.promotions.cupones import validar_cupon


class ValidacionCuponTests(TestCase):
    def crear_cupon(self, **cambios):
        ahora = timezone.now()
        datos = {
            'codigo': 'PRUEBA10',
            'tipo_descuento': Cupon.TipoDescuento.PORCENTAJE,
            'monto': Decimal('10.00'),
            'activo': True,
            'valido_desde': ahora - timedelta(days=1),
            'valido_hasta': ahora + timedelta(days=1),
            'total_minimo': Decimal('0.00'),
        }
        datos.update(cambios)
        return Cupon.objects.create(**datos)

    def test_codigo_ignora_mayusculas_y_espacios_exteriores(self):
        cupon = self.crear_cupon()

        resultado = validar_cupon('  prueba10  ', Decimal('200.00'))

        self.assertTrue(resultado.valido)
        self.assertEqual(resultado.cupon, cupon)
        self.assertEqual(resultado.descuento, Decimal('20.00'))
        self.assertEqual(resultado.motivo, '')

    def test_codigo_inexistente_tiene_motivo_propio(self):
        resultado = validar_cupon('NO-EXISTE', Decimal('100.00'))

        self.assertFalse(resultado.valido)
        self.assertEqual(resultado.descuento, Decimal('0'))
        self.assertEqual(resultado.motivo, 'El cupón no existe.')

    def test_cupon_inactivo_tiene_motivo_propio(self):
        self.crear_cupon(activo=False)

        resultado = validar_cupon('PRUEBA10', Decimal('100.00'))

        self.assertFalse(resultado.valido)
        self.assertEqual(resultado.motivo, 'El cupón está inactivo.')

    def test_cupon_que_aun_no_inicia_tiene_motivo_propio(self):
        self.crear_cupon(valido_desde=timezone.now() + timedelta(days=1))

        resultado = validar_cupon('PRUEBA10', Decimal('100.00'))

        self.assertFalse(resultado.valido)
        self.assertEqual(resultado.motivo, 'El cupón todavía no está vigente.')

    def test_cupon_vencido_tiene_motivo_propio(self):
        self.crear_cupon(valido_hasta=timezone.now() - timedelta(seconds=1))

        resultado = validar_cupon('PRUEBA10', Decimal('100.00'))

        self.assertFalse(resultado.valido)
        self.assertEqual(resultado.motivo, 'El cupón venció.')

    def test_compra_minima_tiene_motivo_propio(self):
        self.crear_cupon(total_minimo=Decimal('300.00'))

        resultado = validar_cupon('PRUEBA10', Decimal('299.99'))

        self.assertFalse(resultado.valido)
        self.assertEqual(
            resultado.motivo,
            'La compra mínima para este cupón es de $300.00.',
        )

    def test_descuento_fijo_no_supera_subtotal(self):
        self.crear_cupon(
            codigo='FIJO',
            tipo_descuento=Cupon.TipoDescuento.FIJO,
            monto=Decimal('500.00'),
        )

        resultado = validar_cupon('FIJO', Decimal('120.00'))

        self.assertTrue(resultado.valido)
        self.assertEqual(resultado.descuento, Decimal('120.00'))

    def test_descuento_fijo_devuelve_el_monto_configurado(self):
        self.crear_cupon(
            codigo='AHORRA',
            tipo_descuento=Cupon.TipoDescuento.FIJO,
            monto=Decimal('200.00'),
        )

        resultado = validar_cupon('AHORRA', Decimal('1000.00'))

        self.assertTrue(resultado.valido)
        self.assertEqual(resultado.descuento, Decimal('200.00'))
