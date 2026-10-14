from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import (
    GRUPO_ALMACEN, GRUPO_CLIENTE, ROL_ADMINISTRADOR, ROL_ALMACEN, ROL_CLIENTE, rol_de,
)
from apps.catalog.models import Categoria, ItemStock, Producto, Variante

CLAVE = 'clave-de-prueba-2026'


class CuentasTests(TestCase):
    """Comprueba el registro, el ingreso y los roles sin bloquear la tienda."""

    def datos_registro(self, **cambios):
        datos = {
            'username': 'compradora',
            'email': 'compradora@ejemplo.com',
            'password1': CLAVE,
            'password2': CLAVE,
        }
        datos.update(cambios)
        return datos

    def crear_variante(self):
        categoria = Categoria.objects.create(nombre='Ropa', slug='ropa')
        producto = Producto.objects.create(
            categoria=categoria, nombre='Camisa', slug='camisa',
            precio=Decimal('1000.00'), activo=True,
        )
        variante = Variante.objects.create(producto=producto, nombre='M')
        ItemStock.objects.create(variante=variante, cantidad=5)
        return variante

    def test_la_migracion_crea_los_grupos_de_roles(self):
        self.assertTrue(Group.objects.filter(name=GRUPO_CLIENTE).exists())
        self.assertTrue(Group.objects.filter(name=GRUPO_ALMACEN).exists())

    def test_registro_guarda_el_usuario_como_cliente_e_inicia_sesion(self):
        respuesta = self.client.post(reverse('accounts:registro'), self.datos_registro())

        self.assertRedirects(respuesta, reverse('catalog:inicio'))
        usuario = User.objects.get(username='compradora')
        self.assertEqual(usuario.email, 'compradora@ejemplo.com')
        self.assertTrue(usuario.check_password(CLAVE))
        self.assertFalse(usuario.is_staff)
        self.assertEqual(rol_de(usuario), ROL_CLIENTE)
        self.assertTrue(usuario.groups.filter(name=GRUPO_CLIENTE).exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), usuario.pk)

    def test_registro_rechaza_claves_distintas_y_correo_repetido(self):
        distintas = self.client.post(
            reverse('accounts:registro'),
            self.datos_registro(password2='otra-clave-2026'),
        )
        self.assertEqual(distintas.status_code, 200)
        self.assertFalse(User.objects.filter(username='compradora').exists())

        User.objects.create_user('primera', 'compradora@ejemplo.com', CLAVE)
        repetido = self.client.post(reverse('accounts:registro'), self.datos_registro())
        self.assertContains(repetido, 'Ya existe una cuenta con ese correo.')
        self.assertFalse(User.objects.filter(username='compradora').exists())

    def test_ingresar_y_salir(self):
        User.objects.create_user('compradora', 'compradora@ejemplo.com', CLAVE)

        mala = self.client.post(
            reverse('accounts:ingresar'),
            {'username': 'compradora', 'password': 'incorrecta'},
        )
        self.assertEqual(mala.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

        buena = self.client.post(
            reverse('accounts:ingresar'),
            {'username': 'compradora', 'password': CLAVE},
        )
        self.assertRedirects(buena, reverse('catalog:inicio'))
        self.assertIn('_auth_user_id', self.client.session)

        # Salir solo funciona por POST: un enlace GET no cierra la sesión.
        self.assertEqual(self.client.get(reverse('accounts:salir')).status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)
        self.client.post(reverse('accounts:salir'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_el_carrito_se_conserva_al_ingresar_y_al_salir(self):
        variante = self.crear_variante()
        User.objects.create_user('compradora', 'compradora@ejemplo.com', CLAVE)
        self.client.post(reverse('cart:agregar'), {'variante_id': variante.pk, 'cantidad': '2'})
        esperado = {str(variante.pk): 2}

        self.client.post(
            reverse('accounts:ingresar'),
            {'username': 'compradora', 'password': CLAVE},
        )
        self.assertEqual(self.client.session['carrito'], esperado)

        self.client.post(reverse('accounts:salir'))
        self.assertEqual(self.client.session['carrito'], esperado)

    def test_ingresar_no_redirige_a_otro_sitio(self):
        User.objects.create_user('compradora', 'compradora@ejemplo.com', CLAVE)
        respuesta = self.client.post(
            reverse('accounts:ingresar'),
            {'username': 'compradora', 'password': CLAVE, 'next': 'https://otro-sitio.example/'},
        )
        self.assertRedirects(respuesta, reverse('catalog:inicio'))

    def test_roles_y_boton_de_administracion(self):
        cliente = User.objects.create_user('cliente', 'cliente@ejemplo.com', CLAVE)
        almacen = User.objects.create_user('almacen', 'almacen@ejemplo.com', CLAVE)
        almacen.groups.add(Group.objects.get(name=GRUPO_ALMACEN))
        administrador = User.objects.create_user(
            'jefa', 'jefa@ejemplo.com', CLAVE, is_staff=True, is_superuser=True,
        )

        self.assertEqual(rol_de(cliente), ROL_CLIENTE)
        self.assertEqual(rol_de(almacen), ROL_ALMACEN)
        self.assertEqual(rol_de(administrador), ROL_ADMINISTRADOR)

        enlace_admin = reverse('admin:index')
        visitante = self.client.get(reverse('catalog:inicio'))
        self.assertContains(visitante, reverse('accounts:ingresar'))
        self.assertContains(visitante, reverse('accounts:registro'))
        self.assertNotContains(visitante, enlace_admin)

        self.client.force_login(cliente)
        self.assertNotContains(self.client.get(reverse('catalog:inicio')), enlace_admin)

        self.client.force_login(administrador)
        pagina = self.client.get(reverse('catalog:inicio'))
        self.assertContains(pagina, enlace_admin)
        self.assertContains(pagina, ROL_ADMINISTRADOR)

    def test_la_tienda_y_el_almacen_no_exigen_iniciar_sesion(self):
        for nombre in ['catalog:inicio', 'cart:ver', 'warehouse:lista']:
            with self.subTest(pagina=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)
