from decimal import Decimal
from html.parser import HTMLParser

from django.test import Client, TestCase
from django.urls import reverse

from .models import Categoria, ImagenProducto, ItemStock, Producto, Variante


class ElementosFormulario(HTMLParser):
    """Lee atributos del HTML para comprobar el formulario que recibe el navegador."""

    def __init__(self):
        super().__init__()
        self.elementos = []

    def handle_starttag(self, etiqueta, atributos):
        self.elementos.append((etiqueta, dict(atributos)))


class DetalleProductoTests(TestCase):
    """Comprueba el detalle y su conexión con el carrito en una base temporal."""

    @classmethod
    def setUpTestData(cls):
        # Crear casos independientes de los datos que cada integrante cambia en el admin.
        cls.categoria = Categoria.objects.create(nombre='Ropa', slug='ropa')
        cls.producto = Producto.objects.create(
            categoria=cls.categoria, nombre='Camiseta de prueba', slug='camiseta-prueba',
            descripcion='Primera línea.\n\nSegunda línea.', precio=Decimal('100.00'),
            precio_oferta=Decimal('80.00'),
        )
        cls.disponible = Variante.objects.create(producto=cls.producto, nombre='M / Rojo')
        cls.agotada = Variante.objects.create(producto=cls.producto, nombre='L / Azul')
        cls.sin_stock = Variante.objects.create(producto=cls.producto, nombre='S / Verde')
        ItemStock.objects.create(variante=cls.disponible, cantidad=5)
        ItemStock.objects.create(variante=cls.agotada, cantidad=0)
        cls.producto_unico = Producto.objects.create(
            categoria=cls.categoria, nombre='Gorra', slug='gorra', precio=Decimal('50.00'),
        )
        cls.unica = Variante.objects.create(producto=cls.producto_unico, nombre='Única')
        ItemStock.objects.create(variante=cls.unica, cantidad=3)

    def detalle(self, producto=None, cliente=None):
        producto = producto or self.producto
        return (cliente or self.client).get(reverse('catalog:producto', args=[producto.slug]))

    def elementos(self, respuesta, etiqueta):
        parser = ElementosFormulario()
        parser.feed(respuesta.content.decode())
        return [atributos for nombre, atributos in parser.elementos if nombre == etiqueta]

    def test_detalle_muestra_datos_categoria_y_oferta(self):
        respuesta = self.detalle()
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'catalog/producto.html')
        self.assertContains(respuesta, self.producto.nombre)
        self.assertContains(respuesta, '<p>Primera línea.</p>', html=True)
        self.assertContains(respuesta, reverse('catalog:categoria', args=['ropa']))
        self.assertContains(respuesta, '<del class="text-muted me-2">100,00</del>', html=True)
        self.assertContains(respuesta, '<strong>80,00</strong>', html=True)

    def test_inactivo_e_inexistente_responden_404(self):
        self.producto.activo = False
        self.producto.save(update_fields=['activo'])
        self.assertEqual(self.detalle().status_code, 404)
        self.assertEqual(self.client.get(reverse('catalog:producto', args=['no-existe'])).status_code, 404)

    def test_todas_las_imagenes_con_textos_alternativos(self):
        for numero in (1, 2):
            ImagenProducto.objects.create(
                producto=self.producto, imagen=f'productos/prueba-{numero}.png',
                texto_alternativo=f'Vista {numero}',
            )
        imagenes = self.elementos(self.detalle(), 'img')
        self.assertEqual(len(imagenes), 2)
        self.assertEqual([imagen['alt'] for imagen in imagenes], ['Vista 1', 'Vista 2'])

    def test_sin_imagenes_y_sin_descripcion_muestra_avisos(self):
        self.producto.descripcion = ''
        self.producto.save(update_fields=['descripcion'])
        respuesta = self.detalle()
        self.assertContains(respuesta, 'No hay imágenes disponibles')
        self.assertContains(respuesta, 'No hay descripción disponible')

    def test_variantes_agotadas_o_sin_registro_stock_no_se_pueden_elegir(self):
        opciones = {opcion['value']: opcion for opcion in self.elementos(self.detalle(), 'option')}
        self.assertNotIn('disabled', opciones[str(self.disponible.pk)])
        self.assertIn('disabled', opciones[str(self.agotada.pk)])
        self.assertIn('disabled', opciones[str(self.sin_stock.pk)])

    def test_producto_totalmente_agotado_no_tiene_formulario_de_compra(self):
        ItemStock.objects.filter(variante=self.disponible).update(cantidad=0)
        respuesta = self.detalle()
        self.assertContains(respuesta, '<strong>Agotado</strong>', html=True)
        self.assertNotContains(respuesta, 'Agregar al carrito')
        self.assertFalse(self.elementos(respuesta, 'select'))

    def test_producto_sin_variantes_se_muestra_como_agotado(self):
        self.producto_unico.variantes.all().delete()
        respuesta = self.detalle(self.producto_unico)
        self.assertContains(respuesta, '<strong>Agotado</strong>', html=True)
        self.assertNotContains(respuesta, 'Agregar al carrito')

    def test_producto_con_variante_unica_tiene_selector_funcional(self):
        respuesta = self.detalle(self.producto_unico)
        self.assertContains(respuesta, 'Única')
        opciones = self.elementos(respuesta, 'option')
        opcion = next(opcion for opcion in opciones if opcion['value'] == str(self.unica.pk))
        self.assertNotIn('disabled', opcion)
        self.assertContains(respuesta, 'Agregar al carrito')

    def test_formulario_envia_campos_acordados_con_csrf(self):
        respuesta = self.detalle()
        formularios = self.elementos(respuesta, 'form')
        compra = next(f for f in formularios if f.get('action') == reverse('cart:agregar'))
        self.assertEqual(compra['method'], 'post')
        entradas = {e['name']: e for e in self.elementos(respuesta, 'input') if 'name' in e}
        self.assertTrue(entradas['csrfmiddlewaretoken']['value'])
        self.assertEqual(entradas['cantidad']['min'], '1')
        self.assertEqual(entradas['cantidad']['step'], '1')
        self.assertEqual(self.elementos(respuesta, 'select')[0]['name'], 'variante_id')

    def test_agregar_al_carrito_con_csrf_sin_descontar_inventario(self):
        # Usar el token que genera la página, igual que un navegador real.
        cliente = Client(enforce_csrf_checks=True)
        respuesta = self.detalle(cliente=cliente)
        token = next(e['value'] for e in self.elementos(respuesta, 'input')
                     if e.get('name') == 'csrfmiddlewaretoken')
        respuesta = cliente.post(reverse('cart:agregar'), {
            'csrfmiddlewaretoken': token, 'variante_id': self.disponible.pk, 'cantidad': 2,
        })
        self.assertRedirects(respuesta, reverse('cart:ver'))
        self.assertEqual(cliente.session['carrito'], {str(self.disponible.pk): 2})
        self.assertEqual(ItemStock.objects.get(variante=self.disponible).cantidad, 5)
        self.assertContains(cliente.get(reverse('cart:ver')), self.producto.nombre)

    def test_post_sin_csrf_es_rechazado(self):
        cliente = Client(enforce_csrf_checks=True)
        respuesta = cliente.post(reverse('cart:agregar'), {
            'variante_id': self.disponible.pk, 'cantidad': 1,
        })
        self.assertEqual(respuesta.status_code, 403)
        self.assertFalse(cliente.session.get('carrito'))

    def test_cantidades_invalidas_y_variantes_agotadas_no_agregan_productos(self):
        casos = [(self.disponible, valor) for valor in ('0', '-1', '1.5', 'abc', '6')]
        casos += [(self.agotada, '1'), (self.sin_stock, '1')]
        for variante, cantidad in casos:
            with self.subTest(variante=variante.nombre, cantidad=cantidad):
                cliente = Client()
                respuesta = cliente.post(reverse('cart:agregar'), {
                    'variante_id': variante.pk, 'cantidad': cantidad,
                }, follow=True)
                self.assertEqual(respuesta.status_code, 200)
                self.assertFalse(cliente.session.get('carrito'))
                self.assertTrue(list(respuesta.context['messages']))

    def test_bajar_stock_o_desactivar_despues_de_abrir_detalle_bloquea_compra(self):
        self.detalle()
        ItemStock.objects.filter(variante=self.disponible).update(cantidad=0)
        self.client.post(reverse('cart:agregar'), {'variante_id': self.disponible.pk, 'cantidad': 1})
        self.assertFalse(self.client.session.get('carrito'))
        ItemStock.objects.filter(variante=self.disponible).update(cantidad=5)
        self.producto.activo = False
        self.producto.save(update_fields=['activo'])
        self.client.post(reverse('cart:agregar'), {'variante_id': self.disponible.pk, 'cantidad': 1})
        self.assertFalse(self.client.session.get('carrito'))
