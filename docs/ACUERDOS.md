# ACUERDOS DEL EQUIPO

Este archivo es el **contrato** del proyecto. Los tres trabajamos con los mismos nombres, las mismas carpetas y las mismas rutas. Si cada uno (o su IA) inventa los suyos, el proyecto no encaja al unirlo.

> **Regla de oro:** antes de pedirle algo a tu IA, pégale este archivo completo y dile: *"respeta estos acuerdos, no cambies nombres ni agregues librerías"*.
> Si la IA te propone algo distinto a lo que dice aquí, gana este archivo.

Solo Vicente edita la carpeta `docs/`. Si crees que un acuerdo está mal, avísale; no lo cambies por tu cuenta.

---

## 1. Qué pide el profesor (resumen)

Un e-commerce hecho con **Django puro** (templates, models, views, forms, ORM, urls). Sin login de compradores.

El flujo completo es este, y es lo que más vale en la nota:

1. El comprador ve la **tienda**: productos destacados, en oferta, por categoría y con búsqueda.
2. Entra a un **producto**: ve detalle, imágenes, elige variante (talla/color) y cantidad, y lo agrega al carrito.
3. En el **carrito** cambia cantidades, elimina productos y aplica un **cupón**.
4. En el **checkout** llena sus datos de envío y confirma. Se crea la **orden** con sus líneas.
5. En el **almacén** se ven las órdenes listas, se abre el detalle y se **despacha**: baja el inventario y la orden cambia de estado.

Entregables: repositorio con commits significativos, README, carpeta `base_de_datos/` con fixtures, y demo en local o video.

## 2. Decisiones técnicas (ya tomadas, no se discuten en el código)

El documento del profesor deja huecos. Estas son las decisiones para llenarlos. Van también al README final.

| # | Decisión | Por qué |
|---|----------|---------|
| D1 | **Todo producto tiene al menos una variante.** Si no tiene tallas ni colores, tiene una sola variante llamada `Única`. | El carrito, la orden y el inventario siempre apuntan a una **variante**. Así no hay que preguntar "¿es producto o variante?" en cada parte del código. |
| D2 | El **carrito vive en la sesión**, no en la base de datos. | El profesor lo permite, es más simple y sirve para explicar sesiones en el README. |
| D3 | El carrito guarda solo **id de variante y cantidad**. El precio se lee siempre de la base de datos. | Evita precios viejos o manipulados. |
| D4 | Se agrega el campo `precio_oferta` a Producto. | El profesor pide mostrar productos "en oferta" pero su modelo no trae cómo saberlo. |
| D5 | Se agrega la relación `categoria` a Producto. | El profesor pide listar por categoría pero su modelo no la conecta. |
| D6 | No hay pago. Al confirmar el checkout la orden nace en estado `READY_TO_SHIP`. | El profesor no pide pasarela de pago. |
| D7 | El inventario **baja al despachar**, no al comprar. En carrito y checkout solo se **valida** que haya suficiente. | Es lo que describe el documento: el botón Despachar registra el movimiento. |
| D8 | Los estados de la orden se escriben tal cual el documento: `READY_TO_SHIP` y `DESPATCHED`. | Para que el profesor encuentre lo que pidió. |
| D9 | Los datos de catálogo y cupones se cargan desde el **admin de Django**. | Ahorra hacer pantallas de administración que nadie pidió. "Sin autenticación" se refiere a los compradores. |
| D10 | Diseño con **Bootstrap 5 por CDN**, más un archivo `static/css/estilos.css` para lo propio. | Tres personas con tres IA distintas producen tres estilos distintos. Bootstrap nos da una base común y responsive. |
| D11 | **Vistas como funciones**, no clases. | Es lo que enseñó el profesor. |

## 3. Versiones y librerías

- Python 3.10 o superior.
- Django 5.2 y Pillow (para imágenes). Nada más.
- Base de datos: SQLite3.
- **Prohibido** agregar librerías sin aprobación de Vicente (nada de DRF, crispy-forms, React, Tailwind, etc.).

## 4. Estructura de carpetas

```
ecommerce-django/
├── manage.py
├── requirements.txt
├── README.md
├── config/                 ← settings.py, urls.py, wsgi.py   (dueño: Vicente)
├── apps/
│   ├── catalog/            ← productos y categorías
│   ├── cart/               ← carrito en sesión
│   ├── promotions/         ← cupones
│   ├── orders/             ← checkout y órdenes
│   └── warehouse/          ← almacén
├── templates/
│   └── base.html           ← plantilla madre                 (dueño: Vicente)
├── static/css/estilos.css
├── media/                  ← imágenes de productos
├── base_de_datos/          ← fixtures (.json)
└── docs/                   ← estos documentos                (dueño: Vicente)
```

Las plantillas de cada app van en `apps/<app>/templates/<app>/archivo.html`. Ejemplo: `apps/cart/templates/cart/carrito.html`. Todas heredan de `base.html`.

## 5. Quién es dueño de qué

Solo el dueño modifica sus archivos. Esto es lo que evita los conflictos al unir ramas.

| Archivos | Dueño |
|----------|-------|
| `config/`, `templates/base.html`, `requirements.txt`, `.gitignore`, `docs/`, `base_de_datos/` | Vicente |
| **Todos** los `models.py`, `admin.py` y carpetas `migrations/` | Vicente |
| `apps/catalog/` (vistas, urls, plantillas) | Frandy |
| `apps/warehouse/` (vistas, urls, plantillas) | Frandy |
| `apps/cart/` | Claudio |
| `apps/promotions/` (lógica de validación) | Claudio |
| `apps/orders/` (vistas, forms, urls, plantillas) | Claudio |
| `static/css/estilos.css` | Frandy (los demás le piden cambios) |

**Si necesitas un cambio en un archivo que no es tuyo** (un campo nuevo en un modelo, un enlace en el menú): pídeselo al dueño. No lo edites tú.

**Nadie corre `makemigrations` excepto Vicente.** Si tu `git status` muestra un archivo nuevo dentro de `migrations/`, no lo subas y avisa.

## 6. Modelos

Vicente los escribe todos en el plan `V-02`. Los demás los **usan** con estos nombres exactos.

### apps/catalog

| Modelo | Campos |
|--------|--------|
| `Categoria` | `nombre`, `slug` (único), `padre` (otra Categoria, opcional) |
| `Producto` | `categoria`, `nombre`, `slug` (único), `descripcion`, `precio`, `precio_oferta` (opcional), `destacado` (sí/no), `activo` (sí/no), `fecha_creacion` |
| `ImagenProducto` | `producto`, `imagen`, `texto_alternativo` |
| `Variante` | `producto`, `nombre` (ej. `M / Rojo`, o `Única`) |
| `ItemStock` | `variante` (una sola fila por variante), `cantidad` |

- Un producto está **en oferta** si `precio_oferta` tiene valor.
- El **precio que se cobra** es `precio_oferta` si existe; si no, `precio`. Producto tendrá una propiedad `precio_final` que devuelve eso. Usen siempre `precio_final`.
- Solo se muestran y se venden productos con `activo` en sí.

### apps/promotions

| Modelo | Campos |
|--------|--------|
| `Cupon` | `codigo` (único, en MAYÚSCULAS), `tipo_descuento` (`PORCENTAJE` o `FIJO`), `monto`, `activo`, `valido_desde`, `valido_hasta`, `total_minimo` |

### apps/orders

| Modelo | Campos |
|--------|--------|
| `Orden` | `clave_sesion`, `nombre_envio`, `direccion_envio`, `telefono`, `estado` (`READY_TO_SHIP` o `DESPATCHED`), `subtotal`, `descuento`, `total`, `cupon` (opcional), `fecha_creacion` |
| `ItemOrden` | `orden`, `variante`, `cantidad`, `precio_unitario`, `total_linea` |

- `subtotal` = suma de las líneas. `total` = `subtotal` − `descuento`. Nunca menor que cero.
- `precio_unitario` es una **copia** del precio en el momento de la compra. Si mañana cambia el precio del producto, la orden no cambia.

### apps/warehouse

| Modelo | Campos |
|--------|--------|
| `MovimientoInventario` | `variante`, `tipo` (`ENTRADA` o `SALIDA`), `cantidad`, `motivo`, `orden_relacionada` (opcional), `fecha_creacion` |
| `Despacho` | `orden` (un solo despacho por orden), `fecha_despacho` |

### apps/cart (sin modelos)

El carrito se guarda en la sesión con estas claves exactas:

| Clave en `request.session` | Contenido |
|----------------------------|-----------|
| `carrito` | Diccionario: id de variante (como texto) → cantidad. Ej.: `{"12": 2, "30": 1}` |
| `cupon_codigo` | Texto con el código del cupón aplicado. No existe si no hay cupón. |

## 7. Rutas (URLs)

Vicente crea **todas** estas rutas en el plan `V-01` apuntando a una página de "En construcción". Cada dueño reemplaza la suya por la real. Así los enlaces entre páginas nunca se rompen aunque el compañero no haya terminado.

En las plantillas se enlaza **siempre por nombre**, nunca escribiendo la ruta a mano.

| Ruta | Nombre | Método | Dueño |
|------|--------|--------|-------|
| `/` | `catalog:inicio` | GET | Frandy |
| `/categoria/<slug>/` | `catalog:categoria` | GET | Frandy |
| `/buscar/` (recibe `?q=texto`) | `catalog:buscar` | GET | Frandy |
| `/producto/<slug>/` | `catalog:producto` | GET | Frandy |
| `/carrito/` | `cart:ver` | GET | Claudio |
| `/carrito/agregar/` | `cart:agregar` | POST | Claudio |
| `/carrito/actualizar/` | `cart:actualizar` | POST | Claudio |
| `/carrito/eliminar/` | `cart:eliminar` | POST | Claudio |
| `/carrito/cupon/` | `cart:aplicar_cupon` | POST | Claudio |
| `/carrito/cupon/quitar/` | `cart:quitar_cupon` | POST | Claudio |
| `/checkout/` | `orders:checkout` | GET y POST | Claudio |
| `/orden/<int:orden_id>/confirmada/` | `orders:confirmacion` | GET | Claudio |
| `/almacen/` | `warehouse:lista` | GET | Frandy |
| `/almacen/orden/<int:orden_id>/` | `warehouse:detalle` | GET | Frandy |
| `/almacen/orden/<int:orden_id>/despachar/` | `warehouse:despachar` | POST | Frandy |
| `/admin/` | (admin de Django) | — | Vicente |

### Campos que envían los formularios

Aquí se conectan el trabajo de Frandy y el de Claudio. Los nombres deben ser idénticos.

| Ruta | Campos del formulario (`name`) |
|------|-------------------------------|
| `cart:agregar` | `variante_id`, `cantidad` |
| `cart:actualizar` | `variante_id`, `cantidad` |
| `cart:eliminar` | `variante_id` |
| `cart:aplicar_cupon` | `codigo` |
| `orders:checkout` | `nombre_envio`, `direccion_envio`, `telefono` |

## 8. Reglas de código

1. Todo lo que **cambia datos** (agregar, eliminar, despachar, confirmar) va por **POST** con su token CSRF. Nunca por un enlace GET.
2. Después de un POST correcto, **redirigir** (no pintar la página directamente). Así recargar no repite la acción.
3. Los avisos de éxito y error usan el **sistema de mensajes de Django**. `base.html` ya los muestra; ustedes solo los crean en la vista.
4. Nombres de modelos, campos, vistas y variables en **español**, como en este documento. Nombres de apps en inglés, como los puso el profesor.
5. Si algo no existe (producto, orden), se responde con **404**, no con un error 500.
6. Nada de datos de prueba "quemados" en las vistas. Los datos salen de la base de datos.
7. No subir `db.sqlite3`, `.venv/` ni `__pycache__/`. El `.gitignore` ya lo evita.

## 9. Si algo sale mal

- **No entiendo mi tarea:** pregunta en el grupo antes de programar. Una pregunta cuesta dos minutos; rehacer un plan cuesta días.
- **Mi IA me dio algo diferente a los acuerdos:** se descarta. Pídele de nuevo pegándole este archivo.
- **Rompí algo y no sé volver atrás:** no borres la carpeta ni fuerces nada. Escribe a Vicente con el mensaje de error.
- **No voy a llegar a tiempo:** avisa apenas lo sepas. Los planes son independientes y se pueden reasignar por su código.
