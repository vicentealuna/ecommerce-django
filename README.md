# E-commerce en Django

Tienda en línea hecha con Django, sin cuentas de comprador. Permite recorrer un catálogo, agregar productos a un carrito guardado en la sesión, aplicar cupones de descuento, confirmar la compra y despachar las órdenes desde una pantalla de almacén que descuenta el inventario.

Proyecto final del curso de Django.

- **Entrega:** 19 de octubre de 2026

## Equipo

| Integrante | Responsabilidades |
|------------|-------------------|
| Vicente Luna | Repositorio, revisión de Pull Requests, esqueleto del proyecto, modelos, admin, datos de ejemplo y README. |
| Frandy Torres | Catálogo y almacén: vistas, rutas y plantillas; estilos CSS y pulido visual responsive. |
| Claudio | Carrito, cupones, checkout y órdenes; pruebas del flujo completo. |

## Requisitos

- Python 3.13
- Git

Las librerías (Django 5.2 y Pillow) se instalan desde `requirements.txt` en el paso 4.

## Cómo correr el proyecto

Los comandos están escritos para Windows. Se ejecutan en orden, desde una terminal.

**1. Clonar el repositorio y entrar a la carpeta**

```bash
git clone https://github.com/vicentealuna/ecommerce-django.git
```

```bash
cd ecommerce-django
```

**2. Crear el entorno virtual**

```bash
python -m venv .venv
```

**3. Activar el entorno virtual**

En PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Si PowerShell da un error de permisos, usar la terminal **cmd** con este comando:

```bash
.venv\Scripts\activate.bat
```

En Linux o macOS:

```bash
source .venv/bin/activate
```

El entorno está activo cuando la línea de la terminal empieza con `(.venv)`.

**4. Instalar las dependencias**

```bash
pip install -r requirements.txt
```

**5. Crear la base de datos**

La base de datos no viene en el repositorio. Este comando la crea con todas sus tablas:

```bash
python manage.py migrate
```

**6. Cargar los datos de ejemplo**

Carga categorías, productos, variantes, inventario, cupones y tres órdenes listas para despachar:

```bash
python manage.py loaddata base_de_datos/datos_iniciales.json
```

Las imágenes de los productos ya vienen en el repositorio, en `media/productos/`. No hay que descargar nada más.

**7. Arrancar el servidor**

```bash
python manage.py runserver
```

Abrir `http://127.0.0.1:8000/` en el navegador.

## Cómo entrar al admin

Los usuarios no viajan en el repositorio. Para entrar al admin hay que crear uno propio:

```bash
python manage.py createsuperuser
```

Luego entrar a `http://127.0.0.1:8000/admin/` con ese usuario.

Desde el admin se administran las categorías, los productos (con sus imágenes y variantes en la misma pantalla), el inventario, los cupones y las órdenes. Los compradores no necesitan cuenta: "sin autenticación" se refiere a ellos, no al administrador.

## Datos de ejemplo para probar

Después del paso 6 la tienda ya tiene datos pensados para probar cada caso.

**Productos**

| Para probar | Usar |
|-------------|------|
| Producto con varias variantes | Camiseta básica de algodón, Pantalón jean clásico, Tenis deportivos |
| Producto con una sola variante (`Única`) | Gorra clásica, Mochila urbana |
| Producto en oferta | Camiseta estampada, Chaqueta impermeable, Sandalias de playa |
| Una variante agotada | Camiseta estampada, variante `L / Azul` |
| Producto totalmente agotado | Cinturón de cuero |
| Producto inactivo (no debe verse en la tienda) | Bufanda de lana |
| Poco inventario | Mochila urbana (3 unidades) |
| Subcategoría | Ropa > Camisetas |

**Cupones**

| Código | Qué hace |
|--------|----------|
| `BIENVENIDO10` | 10 % de descuento |
| `AHORRA200` | 200 de descuento fijo |
| `MINIMO3000` | 500 de descuento, exige una compra mínima de 3000 |
| `VENCIDO15` | Está vencido: debe rechazarse |
| `INACTIVO20` | Está desactivado: debe rechazarse |

**Órdenes en el almacén**

| Orden | Resultado esperado |
|-------|--------------------|
| Orden 1 (Ana Pérez) | Se puede despachar |
| Orden 2 (Luis Gómez) | Se puede despachar |
| Orden 3 (María Santos) | No se puede despachar: pide 5 mochilas y hay 3 |

## Mapa de páginas

**Tienda**

| Ruta | Qué muestra |
|------|-------------|
| `/` | Inicio: categorías, productos destacados y productos en oferta |
| `/categoria/<slug>/` | Productos de una categoría |
| `/buscar/?q=texto` | Resultados de la búsqueda |
| `/producto/<slug>/` | Detalle del producto: imágenes, precio, variantes y formulario para agregar al carrito |

**Compra**

| Ruta | Qué hace |
|------|----------|
| `/carrito/` | Muestra el carrito con sus totales |
| `/carrito/agregar/` | Agrega una variante al carrito (POST) |
| `/carrito/actualizar/` | Cambia la cantidad de una línea (POST) |
| `/carrito/eliminar/` | Quita una línea del carrito (POST) |
| `/carrito/cupon/` | Aplica un cupón (POST) |
| `/carrito/cupon/quitar/` | Quita el cupón aplicado (POST) |
| `/checkout/` | Formulario con los datos de envío y confirmación de la compra |
| `/orden/<id>/confirmada/` | Resumen de la orden recién creada |

**Almacén**

| Ruta | Qué hace |
|------|----------|
| `/almacen/` | Lista de órdenes pendientes de despacho |
| `/almacen/orden/<id>/` | Detalle de la orden con el inventario disponible de cada artículo |
| `/almacen/orden/<id>/despachar/` | Despacha la orden y descuenta el inventario (POST) |

**Administración**

| Ruta | Qué hace |
|------|----------|
| `/admin/` | Admin de Django |

Todo lo que cambia datos va por POST con su token CSRF y termina en una redirección, para que recargar la página no repita la acción.

## Cómo se manejan las sesiones

La tienda no tiene cuentas de comprador. Para saber qué carrito le pertenece a cada visitante se usan las sesiones de Django: el navegador guarda una cookie con un identificador y el servidor guarda los datos de esa sesión en la base de datos.

En la sesión se guardan solo dos cosas:

| Clave | Contenido |
|-------|-----------|
| `carrito` | Un diccionario: id de la variante → cantidad. Ejemplo: `{"12": 2, "30": 1}` |
| `cupon_codigo` | El código del cupón aplicado. No existe si no hay cupón. |

El precio **no** se guarda en la sesión. Cada vez que se muestra el carrito o se confirma la compra, el precio y el inventario se leen de la base de datos. Así el comprador nunca paga un precio viejo ni puede manipularlo.

Al confirmar el checkout, el carrito se convierte en una orden guardada en la base de datos y la sesión se limpia.

**Cómo simular otro comprador**

- Abrir la tienda en una **ventana de incógnito**: es una sesión nueva, con su propio carrito vacío.
- O **borrar las cookies** del sitio en el navegador: el visitante vuelve a empezar sin carrito.

Dos ventanas (una normal y una de incógnito) se comportan como dos compradores distintos, cada uno con su carrito.

## Decisiones técnicas

El documento de requerimientos dejaba algunos puntos abiertos. Estas son las decisiones que tomó el equipo y su motivo.

| # | Decisión | Por qué |
|---|----------|---------|
| D1 | Todo producto tiene al menos una variante. Si no tiene tallas ni colores, tiene una sola variante llamada `Única`. | El carrito, la orden y el inventario siempre apuntan a una variante. Así el código no tiene que preguntar en cada parte si trabaja con un producto o con una variante. |
| D2 | El carrito vive en la sesión, no en la base de datos. | El documento lo permite, es más simple y no obliga a crear cuentas de comprador. |
| D3 | El carrito guarda solo el id de la variante y la cantidad. El precio se lee siempre de la base de datos. | Evita precios viejos o manipulados. |
| D4 | Se agregó el campo `precio_oferta` a Producto. | Se pide mostrar productos en oferta, pero el modelo original no traía cómo saberlo. |
| D5 | Se agregó la relación `categoria` a Producto. | Se pide listar por categoría, pero el modelo original no las conectaba. |
| D6 | No hay pago. Al confirmar el checkout la orden nace en estado `READY_TO_SHIP`. | No se pide pasarela de pago. |
| D7 | El inventario baja al despachar, no al comprar. En el carrito y el checkout solo se valida que haya suficiente. | Es lo que describe el documento: el botón Despachar registra el movimiento de inventario. |
| D8 | Los estados de la orden se escriben tal cual el documento: `READY_TO_SHIP` y `DESPATCHED`. | Para que coincidan con lo pedido. |
| D9 | El catálogo y los cupones se cargan desde el admin de Django. | Evita construir pantallas de administración que no se pidieron. |
| D10 | Diseño con Bootstrap 5 por CDN, más un archivo `static/css/estilos.css` para lo propio. | Da una base común y responsive a un equipo de tres personas. |
| D11 | Vistas como funciones, no como clases. | Es lo que se enseñó en el curso. |

## Estructura del proyecto

```text
ecommerce-django/
├── config/            configuración del proyecto y rutas principales
├── apps/
│   ├── catalog/       categorías, productos, variantes e inventario
│   ├── cart/          carrito en sesión
│   ├── promotions/    cupones y su validación
│   ├── orders/        checkout y órdenes
│   └── warehouse/     almacén y despacho
├── templates/         plantilla base
├── static/css/        estilos propios
├── media/productos/   imágenes de los productos
├── base_de_datos/     datos de ejemplo (fixtures)
└── docs/              acuerdos del equipo, planes y pruebas
```

## Pruebas

Para correr las pruebas automáticas:

```bash
python manage.py test
```

Los casos probados a mano sobre el flujo completo (compra con y sin cupón, cupón inválido, compra por encima del inventario, dos compradores a la vez, despacho correcto y despacho bloqueado) están en [docs/PRUEBAS.md](docs/PRUEBAS.md).

## Demo

La demostración se hace en local. Con el proyecto corriendo (sección "Cómo correr el proyecto"), el recorrido completo es:

1. Entrar a la tienda y abrir un producto.
2. Elegir una variante y agregarla al carrito.
3. Aplicar un cupón de la tabla de datos de ejemplo.
4. Confirmar la compra en el checkout.
5. Entrar al almacén, abrir la orden y despacharla.

## Qué hizo cada integrante

**Vicente Luna**

- Creó y configuró el repositorio, las reglas de trabajo con ramas y Pull Requests, y las revisiones automáticas.
- Armó el esqueleto del proyecto: configuración, las cinco apps, las rutas y la plantilla base.
- Definió todos los modelos, las migraciones y el admin.
- Cargó los datos de ejemplo y las imágenes.
- Revisó y fusionó los Pull Requests del equipo y escribió este README.

**Frandy Torres**

- Tienda: inicio con destacados y ofertas, categorías y búsqueda.
- Página de producto con imágenes, variantes y formulario de compra.
- Almacén: lista de órdenes pendientes, detalle con inventario y despacho con sus bloqueos.
- Estilos propios y pulido visual responsive de todo el sitio.

**Claudio**

- Carrito en sesión: agregar, actualizar, eliminar, totales y contador en el menú.
- Cupones: validación, cálculo del descuento y mensajes de rechazo.
- Checkout: formulario de envío, creación de la orden y página de confirmación.
- Pruebas del flujo completo, documentadas en `docs/PRUEBAS.md`.
