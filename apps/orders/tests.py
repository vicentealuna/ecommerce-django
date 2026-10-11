from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.db import IntegrityError
from django.contrib.sessions.backends.db import SessionStore
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.catalog.models import Categoria, ItemStock, Producto, Variante
from apps.orders.models import ItemOrden, Orden
from apps.orders.services import crear_orden_desde_carrito
from apps.promotions.models import Cupon


class CheckoutTests(TestCase):
    def setUp(self):
        categoria = Categoria.objects.create(nombre='Ropa', slug='ropa')
        self.producto = Producto.objects.create(
            categoria=categoria,
            nombre='Camisa',
            slug='camisa',
            descripcion='Camisa de prueba',
            precio=Decimal('1000.00'),
            activo=True,
        )
        self.variante = Variante.objects.create(producto=self.producto, nombre='M')
        self.stock = ItemStock.objects.create(variante=self.variante, cantidad=5)
        self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': '2'},
        )

    def datos_checkout(self, **cambios):
        datos = {
            'nombre_envio': 'Claudio Pérez',
            'direccion_envio': 'Calle Principal 123',
            'telefono': '809-555-1212',
        }
        datos.update(cambios)
        return datos

    def crear_cupon(self, **cambios):
        ahora = timezone.now()
        datos = {
            'codigo': 'BIENVENIDO10',
            'tipo_descuento': Cupon.TipoDescuento.PORCENTAJE,
            'monto': Decimal('10.00'),
            'activo': True,
            'valido_desde': ahora - timedelta(days=1),
            'valido_hasta': ahora + timedelta(days=1),
            'total_minimo': Decimal('0.00'),
        }
        datos.update(cambios)
        return Cupon.objects.create(**datos)

    def aplicar_cupon(self, codigo='BIENVENIDO10'):
        return self.client.post(
            reverse('cart:aplicar_cupon'),
            {'codigo': codigo},
        )

    def test_checkout_muestra_formulario_y_resumen(self):
        response = self.client.get(reverse('orders:checkout'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="nombre_envio"')
        self.assertContains(response, 'name="direccion_envio"')
        self.assertContains(response, 'type="tel"')
        self.assertContains(response, 'Camisa')
        self.assertEqual(response.context['subtotal'], Decimal('2000.00'))
        self.assertEqual(response.context['total'], Decimal('2000.00'))

    def test_carrito_vacio_redirige_a_tienda_con_aviso(self):
        self.client.post(reverse('cart:eliminar'), {'variante_id': self.variante.pk})

        response = self.client.get(reverse('orders:checkout'), follow=True)

        self.assertRedirects(response, reverse('catalog:inicio'))
        self.assertContains(response, 'Tu carrito está vacío.')
        self.assertEqual(Orden.objects.count(), 0)

    def test_producto_inactivo_al_abrir_checkout_regresa_al_carrito_con_aviso(self):
        self.producto.activo = False
        self.producto.save(update_fields=['activo'])

        response = self.client.get(reverse('orders:checkout'), follow=True)

        self.assertEqual(Orden.objects.count(), 0)
        self.assertContains(response, 'Un producto del carrito ya no está disponible.')
        self.assertEqual(response.redirect_chain[0][0], reverse('cart:ver'))

    def test_formulario_vacio_muestra_errores_y_no_crea_orden(self):
        response = self.client.post(reverse('orders:checkout'), {})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este campo es obligatorio.', count=3)
        self.assertEqual(Orden.objects.count(), 0)

    def test_telefono_solo_acepta_digitos_espacios_y_guiones(self):
        response = self.client.post(
            reverse('orders:checkout'),
            self.datos_checkout(telefono='809-555-ABCD'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usa únicamente dígitos, espacios y guiones.')
        self.assertEqual(Orden.objects.count(), 0)

    def test_telefono_requiere_largo_razonable(self):
        response = self.client.post(
            reverse('orders:checkout'),
            self.datos_checkout(telefono='123-45'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'entre 7 y 15 dígitos')
        self.assertEqual(Orden.objects.count(), 0)

    def test_compra_crea_orden_lista_y_copia_linea_sin_bajar_inventario(self):
        clave_sesion = self.client.session.session_key

        response = self.client.post(
            reverse('orders:checkout'),
            self.datos_checkout(),
        )

        orden = Orden.objects.get()
        item = orden.items.get()
        self.assertRedirects(
            response,
            reverse('orders:confirmacion', kwargs={'orden_id': orden.pk}),
        )
        self.assertEqual(orden.clave_sesion, clave_sesion)
        self.assertEqual(orden.estado, Orden.Estado.READY_TO_SHIP)
        self.assertEqual(orden.subtotal, Decimal('2000.00'))
        self.assertEqual(orden.descuento, Decimal('0.00'))
        self.assertEqual(orden.total, Decimal('2000.00'))
        self.assertEqual(item.cantidad, 2)
        self.assertEqual(item.precio_unitario, Decimal('1000.00'))
        self.assertEqual(item.total_linea, Decimal('2000.00'))
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.cantidad, 5)
        self.assertNotIn('carrito', self.client.session)
        self.assertNotIn('cupon_codigo', self.client.session)

    def test_compra_guarda_descuento_y_cupon_valido(self):
        cupon = self.crear_cupon()
        self.aplicar_cupon()

        response = self.client.post(
            reverse('orders:checkout'),
            self.datos_checkout(),
        )

        orden = Orden.objects.get()
        self.assertRedirects(
            response,
            reverse('orders:confirmacion', kwargs={'orden_id': orden.pk}),
        )
        self.assertEqual(orden.cupon, cupon)
        self.assertEqual(orden.subtotal, Decimal('2000.00'))
        self.assertEqual(orden.descuento, Decimal('200.00'))
        self.assertEqual(orden.total, Decimal('1800.00'))

    def test_checkout_revalida_cupon_y_rechaza_si_dejo_de_ser_valido(self):
        cupon = self.crear_cupon(total_minimo=Decimal('2500.00'))
        self.client.post(
            reverse('cart:eliminar'),
            {'variante_id': self.variante.pk},
        )
        self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': '3'},
        )
        self.aplicar_cupon()
        cupon.total_minimo = Decimal('3500.00')
        cupon.save(update_fields=['total_minimo'])

        response = self.client.post(
            reverse('orders:checkout'),
            self.datos_checkout(),
            follow=True,
        )

        self.assertEqual(Orden.objects.count(), 0)
        self.assertContains(response, 'La compra mínima para este cupón es de $3500.00.')

    def test_confirmacion_solo_es_visible_en_la_sesion_compradora(self):
        response = self.client.post(
            reverse('orders:checkout'),
            self.datos_checkout(),
        )
        orden = Orden.objects.get()
        url = reverse('orders:confirmacion', kwargs={'orden_id': orden.pk})

        respuesta_comprador = self.client.get(url)
        respuesta_otra_sesion = self.client_class().get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(respuesta_comprador.status_code, 200)
        self.assertContains(respuesta_comprador, f'orden #{orden.pk}')
        self.assertEqual(respuesta_otra_sesion.status_code, 404)

    def test_recargar_confirmacion_no_crea_otra_orden(self):
        self.client.post(
            reverse('orders:checkout'),
            self.datos_checkout(),
        )
        orden = Orden.objects.get()
        url = reverse('orders:confirmacion', kwargs={'orden_id': orden.pk})

        primera = self.client.get(url)
        segunda = self.client.get(url)

        self.assertEqual(primera.status_code, 200)
        self.assertEqual(segunda.status_code, 200)
        self.assertEqual(Orden.objects.count(), 1)

    def test_confirma_inventario_otra_vez_y_no_crea_orden_si_bajo(self):
        self.client.get(reverse('orders:checkout'))
        self.stock.cantidad = 1
        self.stock.save(update_fields=['cantidad'])

        response = self.client.post(
            reverse('orders:checkout'),
            self.datos_checkout(),
            follow=True,
        )

        self.assertEqual(Orden.objects.count(), 0)
        self.assertContains(response, 'Inventario insuficiente para Camisa.')
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.cantidad, 1)

    def test_producto_desactivado_antes_de_confirmar_no_crea_orden(self):
        self.client.get(reverse('orders:checkout'))
        self.producto.activo = False
        self.producto.save(update_fields=['activo'])

        response = self.client.post(
            reverse('orders:checkout'),
            self.datos_checkout(),
            follow=True,
        )

        self.assertEqual(Orden.objects.count(), 0)
        self.assertContains(response, 'Un producto del carrito ya no está disponible.')
        self.assertEqual(response.redirect_chain[0][0], reverse('cart:ver'))

    def test_cambio_de_precio_no_modifica_precio_guardado_en_orden(self):
        self.client.post(
            reverse('orders:checkout'),
            self.datos_checkout(),
        )
        item = ItemOrden.objects.get()
        self.producto.precio = Decimal('1500.00')
        self.producto.save(update_fields=['precio'])

        item.refresh_from_db()

        self.assertEqual(item.precio_unitario, Decimal('1000.00'))
        self.assertEqual(item.total_linea, Decimal('2000.00'))

    def test_fallo_al_crear_lineas_revierte_toda_la_orden(self):
        with patch(
            'apps.orders.services.ItemOrden.objects.bulk_create',
            side_effect=IntegrityError('fallo de prueba'),
        ):
            with self.assertRaises(IntegrityError):
                self.client.post(
                    reverse('orders:checkout'),
                    self.datos_checkout(),
                )

        self.assertEqual(Orden.objects.count(), 0)
        self.assertEqual(ItemOrden.objects.count(), 0)

    def test_checkout_crea_clave_de_sesion_si_aun_no_existe(self):
        sesion = SessionStore()
        sesion['carrito'] = {str(self.variante.pk): 1}

        orden = crear_orden_desde_carrito(sesion, self.datos_checkout())

        self.assertTrue(sesion.session_key)
        self.assertEqual(orden.clave_sesion, sesion.session_key)
        self.assertEqual(orden.estado, Orden.Estado.READY_TO_SHIP)
        self.assertNotIn('carrito', sesion)
