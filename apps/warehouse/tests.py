from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from apps.catalog.models import Categoria, ItemStock, Producto, Variante
from apps.orders.models import ItemOrden, Orden

from .models import Despacho, MovimientoInventario


class AlmacenTests(TestCase):
    """Comprueba el despacho y sus rechazos en una base de datos de pruebas."""

    @classmethod
    def setUpTestData(cls):
        # Crear dos variantes con existencias conocidas e independientes.
        categoria = Categoria.objects.create(nombre='Accesorios', slug='accesorios')
        producto = Producto.objects.create(
            categoria=categoria, nombre='Mochila', slug='mochila', precio=100,
        )
        cls.variante = Variante.objects.create(producto=producto, nombre='Única')
        cls.otra_variante = Variante.objects.create(producto=producto, nombre='Azul')
        ItemStock.objects.create(variante=cls.variante, cantidad=3)
        ItemStock.objects.create(variante=cls.otra_variante, cantidad=20)

    def setUp(self):
        # Cada prueba comienza con una orden nueva y dos unidades pedidas.
        self.orden = Orden.objects.create(
            clave_sesion='sesion-prueba', nombre_envio='Destinatario de prueba',
            direccion_envio='Dirección de prueba', telefono='123456789',
            subtotal=200, total=200,
        )
        self.item = self.agregar_item(self.variante, 2)
        self.ruta = reverse('warehouse:despachar', args=[self.orden.pk])

    def agregar_item(self, variante, cantidad):
        """Añade una línea a la orden usada en la prueba."""
        return ItemOrden.objects.create(
            orden=self.orden, variante=variante, cantidad=cantidad,
            precio_unitario=100, total_linea=100 * cantidad,
        )

    def comprobar_sin_despacho(self):
        """Verifica que un rechazo no cambió estado, inventario ni registros."""
        self.orden.refresh_from_db()
        self.assertEqual(self.orden.estado, Orden.Estado.READY_TO_SHIP)
        self.assertEqual(ItemStock.objects.get(variante=self.variante).cantidad, 3)
        self.assertEqual(ItemStock.objects.get(variante=self.otra_variante).cantidad, 20)
        self.assertFalse(Despacho.objects.exists())
        self.assertFalse(MovimientoInventario.objects.exists())

    def test_despacho_completo_y_mensaje_de_exito(self):
        self.agregar_item(self.otra_variante, 4)
        respuesta = self.client.post(self.ruta, follow=True)
        self.assertRedirects(respuesta, reverse('warehouse:lista'))
        self.assertContains(respuesta, 'despachada correctamente')
        self.orden.refresh_from_db()
        self.assertEqual(self.orden.estado, Orden.Estado.DESPATCHED)
        self.assertEqual(ItemStock.objects.get(variante=self.variante).cantidad, 1)
        self.assertEqual(ItemStock.objects.get(variante=self.otra_variante).cantidad, 16)
        self.assertTrue(Despacho.objects.filter(orden=self.orden).exists())
        movimientos = self.orden.movimientos.order_by('variante_id')
        self.assertEqual(
            list(movimientos.values_list('variante_id', 'cantidad', 'tipo')),
            [(self.variante.pk, 2, MovimientoInventario.Tipo.SALIDA),
             (self.otra_variante.pk, 4, MovimientoInventario.Tipo.SALIDA)],
        )
        self.assertNotIn(self.orden, respuesta.context['ordenes'])

    def test_inventario_insuficiente_no_descuenta_otras_lineas(self):
        self.item.variante = self.otra_variante
        self.item.save()
        self.agregar_item(self.variante, 5)
        respuesta = self.client.post(self.ruta, follow=True)
        self.assertContains(respuesta, 'se necesitan 5 y hay 3')
        self.comprobar_sin_despacho()

    def test_repetir_despacho_no_duplica_descuentos_ni_registros(self):
        self.client.post(self.ruta)
        respuesta = self.client.post(self.ruta, follow=True)
        self.assertContains(respuesta, 'ya no está pendiente')
        self.assertEqual(ItemStock.objects.get(variante=self.variante).cantidad, 1)
        self.assertEqual(Despacho.objects.count(), 1)
        self.assertEqual(MovimientoInventario.objects.count(), 1)
        self.assertContains(respuesta, 'Esta orden ya fue despachada.')
        self.assertNotContains(respuesta, 'Despachar orden')

    def test_get_no_despacha(self):
        self.assertEqual(self.client.get(self.ruta).status_code, 405)
        self.comprobar_sin_despacho()

    def test_orden_vacia_no_se_despacha(self):
        self.orden.items.all().delete()
        respuesta = self.client.post(self.ruta, follow=True)
        self.assertContains(respuesta, 'orden sin artículos')
        self.comprobar_sin_despacho()

    def test_variante_sin_registro_de_inventario_se_considera_agotada(self):
        ItemStock.objects.filter(variante=self.variante).delete()
        respuesta = self.client.post(self.ruta, follow=True)
        self.assertContains(respuesta, 'se necesitan 2 y hay 0')
        self.orden.refresh_from_db()
        self.assertEqual(self.orden.estado, Orden.Estado.READY_TO_SHIP)
        self.assertFalse(Despacho.objects.exists())
        self.assertFalse(MovimientoInventario.objects.exists())

    def test_inventario_exacto_puede_quedar_en_cero(self):
        self.item.cantidad = 3
        self.item.save()
        self.client.post(self.ruta)
        self.assertEqual(ItemStock.objects.get(variante=self.variante).cantidad, 0)
        self.assertTrue(Despacho.objects.filter(orden=self.orden).exists())

    def test_fallo_en_segundo_descuento_deshace_toda_la_transaccion(self):
        # Dos líneas de la misma variante pasan la revisión individual,
        # pero su suma excede el inventario: el segundo descuento debe fallar.
        self.agregar_item(self.variante, 2)
        respuesta = self.client.post(self.ruta, follow=True)
        self.assertContains(respuesta, 'No se despachó ningún artículo')
        self.comprobar_sin_despacho()

    def test_error_al_registrar_despacho_deshace_descuentos_y_movimientos(self):
        # Simular un fallo después de descontar y registrar las salidas.
        with patch(
            'apps.warehouse.views.Despacho.objects.create',
            side_effect=RuntimeError('Fallo de prueba'),
        ):
            with self.assertRaises(RuntimeError):
                self.client.post(self.ruta)
        self.comprobar_sin_despacho()

    def test_orden_inexistente_responde_404(self):
        inexistente = self.orden.pk + 1000
        for nombre in ('warehouse:detalle', 'warehouse:despachar'):
            ruta = reverse(nombre, args=[inexistente])
            if nombre == 'warehouse:despachar':
                respuesta = self.client.post(ruta)
            else:
                respuesta = self.client.get(ruta)
            self.assertEqual(respuesta.status_code, 404)
        self.comprobar_sin_despacho()

    def test_formulario_con_csrf_y_rechazo_si_falta_token(self):
        cliente = Client(enforce_csrf_checks=True)
        respuesta = cliente.get(reverse('warehouse:detalle', args=[self.orden.pk]))
        self.assertContains(respuesta, 'csrfmiddlewaretoken')
        self.assertEqual(cliente.post(self.ruta).status_code, 403)
        self.comprobar_sin_despacho()
        token = cliente.cookies['csrftoken'].value
        respuesta = cliente.post(self.ruta, {'csrfmiddlewaretoken': token})
        self.assertRedirects(respuesta, reverse('warehouse:lista'))
        self.assertTrue(Despacho.objects.filter(orden=self.orden).exists())

    def test_lista_ordenada_con_total_y_detalle_con_datos(self):
        self.agregar_item(self.otra_variante, 4)
        otra = Orden.objects.create(
            clave_sesion='otra', nombre_envio='Otro destinatario',
            direccion_envio='Otra dirección', telefono='987654321',
            subtotal=0, total=0,
        )
        respuesta = self.client.get(reverse('warehouse:lista'))
        ordenes = list(respuesta.context['ordenes'])
        self.assertEqual([orden.pk for orden in ordenes], [self.orden.pk, otra.pk])
        self.assertEqual(ordenes[0].cantidad_articulos, 6)
        self.assertEqual(ordenes[1].cantidad_articulos, 0)
        respuesta = self.client.get(reverse('warehouse:detalle', args=[self.orden.pk]))
        textos = (
            'Destinatario de prueba', 'Dirección de prueba',
            '123456789', 'Mochila', 'Única',
        )
        for texto in textos:
            self.assertContains(respuesta, texto)


class OrdenesDeEjemploTests(TestCase):
    """Verifica el flujo con el fixture del equipo, sin usar la base local."""

    fixtures = ['base_de_datos/datos_iniciales.json']

    def test_ordenes_uno_y_dos_se_despachan_con_descuentos_exactos(self):
        for orden_id in (1, 2):
            orden = Orden.objects.get(pk=orden_id)
            # Guardar las existencias previas para compararlas con cada descuento.
            anteriores = {
                item.variante_id: ItemStock.objects.get(variante=item.variante).cantidad
                for item in orden.items.all()
            }
            respuesta = self.client.post(reverse('warehouse:despachar', args=[orden_id]))
            self.assertRedirects(respuesta, reverse('warehouse:lista'))
            orden.refresh_from_db()
            self.assertEqual(orden.estado, Orden.Estado.DESPATCHED)
            self.assertTrue(Despacho.objects.filter(orden=orden).exists())
            self.assertEqual(orden.movimientos.count(), orden.items.count())
            for item in orden.items.all():
                self.assertEqual(
                    ItemStock.objects.get(variante=item.variante).cantidad,
                    anteriores[item.variante_id] - item.cantidad,
                )

    def test_orden_tres_se_rechaza_sin_cambios(self):
        # Conservar una copia de todas las existencias antes del intento.
        anteriores = list(ItemStock.objects.order_by('pk').values_list('pk', 'cantidad'))
        movimientos = MovimientoInventario.objects.count()
        despachos = Despacho.objects.count()
        respuesta = self.client.post(
            reverse('warehouse:despachar', args=[3]), follow=True,
        )
        self.assertContains(respuesta, 'se necesitan 5 y hay 3')
        self.assertEqual(
            list(ItemStock.objects.order_by('pk').values_list('pk', 'cantidad')),
            anteriores,
        )
        self.assertEqual(MovimientoInventario.objects.count(), movimientos)
        self.assertEqual(Despacho.objects.count(), despachos)
        self.assertEqual(Orden.objects.get(pk=3).estado, Orden.Estado.READY_TO_SHIP)
