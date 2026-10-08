from decimal import Decimal
import re

from django.test import Client, TestCase
from django.urls import reverse

from apps.cart.context_processors import carrito_context
from apps.catalog.models import Categoria, ItemStock, Producto, Variante


class CarritoTests(TestCase):
    def setUp(self):
        categoria = Categoria.objects.create(nombre='Ropa', slug='ropa')
        self.producto = Producto.objects.create(
            categoria=categoria,
            nombre='Camisa',
            slug='camisa',
            descripcion='Camisa de prueba',
            precio=Decimal('1000.00'),
            precio_oferta=Decimal('900.00'),
            activo=True,
        )
        self.variante = Variante.objects.create(producto=self.producto, nombre='M')
        ItemStock.objects.create(variante=self.variante, cantidad=5)

    def test_agregar_misma_variante_suma_cantidades(self):
        url = reverse('cart:agregar')
        primera = self.client.post(url, {'variante_id': self.variante.pk, 'cantidad': '2'})
        segunda = self.client.post(url, {'variante_id': self.variante.pk, 'cantidad': '1'})

        self.assertRedirects(primera, reverse('cart:ver'))
        self.assertRedirects(segunda, reverse('cart:ver'))
        self.assertEqual(self.client.session['carrito'], {str(self.variante.pk): 3})

    def test_agregar_cantidad_invalida_no_modifica_carrito(self):
        self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': '2'},
        )

        response = self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': 'letras'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['carrito'], {str(self.variante.pk): 2})
        self.assertContains(response, 'La cantidad debe ser un número entero mayor que cero.')

    def test_cantidad_negativa_no_modifica_carrito(self):
        self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': '2'},
        )

        response = self.client.post(
            reverse('cart:actualizar'),
            {'variante_id': self.variante.pk, 'cantidad': '-1'},
            follow=True,
        )

        self.assertEqual(self.client.session['carrito'], {str(self.variante.pk): 2})
        self.assertContains(response, 'La cantidad debe ser un número entero mayor que cero.')

    def test_no_permite_superar_inventario_y_conserva_carrito(self):
        self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': '2'},
        )

        response = self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': '4'},
            follow=True,
        )

        self.assertEqual(self.client.session['carrito'], {str(self.variante.pk): 2})
        self.assertContains(response, 'Disponible: 5.')

    def test_no_agrega_producto_inactivo_o_variante_inexistente(self):
        self.producto.activo = False
        self.producto.save(update_fields=['activo'])

        response = self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': '1'},
            follow=True,
        )

        self.assertNotIn('carrito', self.client.session)
        self.assertContains(response, 'Este producto ya no está disponible.')

        respuesta_variante_inexistente = self.client.post(
            reverse('cart:agregar'),
            {'variante_id': 99999, 'cantidad': '1'},
            follow=True,
        )
        self.assertContains(respuesta_variante_inexistente, 'La variante seleccionada no existe.')

    def test_carrito_muestra_precio_final_y_totales(self):
        self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': '2'},
        )

        response = self.client.get(reverse('cart:ver'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['subtotal'], Decimal('1800.00'))
        self.assertContains(response, 'Camisa')
        self.assertContains(response, '1800,00')

    def test_actualizar_a_cero_elimina_la_linea(self):
        self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': '2'},
        )

        response = self.client.post(
            reverse('cart:actualizar'),
            {'variante_id': self.variante.pk, 'cantidad': '0'},
        )

        self.assertRedirects(response, reverse('cart:ver'))
        self.assertEqual(self.client.session['carrito'], {})

    def test_actualizar_cantidad_mayor_al_stock_conserva_cantidad_anterior(self):
        self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': '2'},
        )

        response = self.client.post(
            reverse('cart:actualizar'),
            {'variante_id': self.variante.pk, 'cantidad': '6'},
            follow=True,
        )

        self.assertEqual(self.client.session['carrito'], {str(self.variante.pk): 2})
        self.assertContains(response, 'Disponible: 5.')

    def test_eliminar_quita_linea_y_requiere_post(self):
        self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': '2'},
        )

        respuesta_get = self.client.get(reverse('cart:eliminar'))
        respuesta_post = self.client.post(
            reverse('cart:eliminar'),
            {'variante_id': self.variante.pk},
        )

        self.assertEqual(respuesta_get.status_code, 405)
        self.assertRedirects(respuesta_post, reverse('cart:ver'))
        self.assertEqual(self.client.session['carrito'], {})

    def test_carrito_de_otra_sesion_empieza_vacio(self):
        otro_cliente = Client()
        self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': '2'},
        )

        response = otro_cliente.get(reverse('cart:ver'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tu carrito está vacío.')
        self.assertNotIn('carrito', otro_cliente.session)

    def test_carrito_persiste_entre_solicitudes_de_la_misma_sesion(self):
        self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': '2'},
        )

        primera_visita = self.client.get(reverse('cart:ver'))
        segunda_visita = self.client.get(reverse('cart:ver'))

        self.assertContains(primera_visita, 'Camisa')
        self.assertContains(segunda_visita, 'Camisa')
        self.assertEqual(self.client.session['carrito'], {str(self.variante.pk): 2})

    def test_producto_desactivado_se_limpia_sin_romper_el_carrito(self):
        self.client.post(
            reverse('cart:agregar'),
            {'variante_id': self.variante.pk, 'cantidad': '2'},
        )
        self.producto.activo = False
        self.producto.save(update_fields=['activo'])

        response = self.client.get(reverse('cart:ver'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tu carrito está vacío.')
        self.assertEqual(self.client.session['carrito'], {})

    def test_acciones_de_cambio_exigen_post_y_token_csrf(self):
        cliente_con_csrf = Client(enforce_csrf_checks=True)
        sesion = cliente_con_csrf.session
        sesion['carrito'] = {str(self.variante.pk): 1}
        sesion.save()
        datos = {'variante_id': self.variante.pk, 'cantidad': '2'}

        respuesta_sin_token = cliente_con_csrf.post(reverse('cart:actualizar'), datos)
        self.assertEqual(respuesta_sin_token.status_code, 403)

        pagina_carrito = cliente_con_csrf.get(reverse('cart:ver'))
        coincidencia = re.search(
            r'name="csrfmiddlewaretoken" value="([^"]+)"',
            pagina_carrito.content.decode(),
        )
        self.assertIsNotNone(coincidencia)
        respuesta_con_token = cliente_con_csrf.post(
            reverse('cart:actualizar'),
            datos,
            HTTP_X_CSRFTOKEN=coincidencia.group(1),
        )
        self.assertRedirects(respuesta_con_token, reverse('cart:ver'))

    def test_procesador_de_contexto_cuenta_articulos_de_sesion(self):
        request = type('Request', (), {
            'session': {'carrito': {str(self.variante.pk): 2, 'otra-variante': '3'}},
        })()

        self.assertEqual(carrito_context(request), {'carrito_cantidad': 5})
