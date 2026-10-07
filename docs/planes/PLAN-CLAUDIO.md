# PLAN DE CLAUDIO

Tus planes: `C-00` → `C-01` → `C-02` → `C-03` → `C-04`. Hazlos en ese orden, uno por rama.

Tus archivos: `apps/cart/`, `apps/promotions/` y `apps/orders/` (vistas, forms, urls y plantillas).
**No tocas:** ningún `models.py`, `admin.py`, `migrations/`, `config/`, `templates/base.html`, `static/css/estilos.css`, ni las apps de Frandy.

Antes de empezar lee [`ACUERDOS.md`](../ACUERDOS.md) y [`GUIA-GIT.md`](../GUIA-GIT.md).

Este plan dice **qué** debe quedar funcionando, no trae el código. Investígalo por tu cuenta o con tu IA, pero pégale primero `ACUERDOS.md`. Al final debes poder explicar cada línea que subas: Vicente puede preguntártelo en la revisión.

---

## C-00 — Incorporación

**Fase 0 · Rama:** `claudio/c-00-incorporacion`

**Objetivo:** tener el proyecto funcionando en tu equipo y practicar el ciclo completo de git con algo que no puede romper nada.

**Qué hacer**
1. Sigue la sección 1 de `GUIA-GIT.md` hasta ver la tienda en tu navegador.
2. Entra a `/admin/` con el superusuario que creaste y mira los productos, variantes, inventario y cupones de ejemplo. Entiende cómo se relacionan. Lee también las tablas "Cómo ir de un modelo a otro" y "Datos de ejemplo" de `ACUERDOS.md`.
3. Crea tu rama, y en el archivo `EQUIPO.md` agrega una línea con tu nombre y tus apps.
4. Commit, push y abre el PR.

**Cómo se comprueba**
- [ ] Existe un PR titulado `C-00 Incorporación` desde la rama correcta.
- [ ] El PR solo cambia `EQUIPO.md`.
- [ ] El commit sale con tu nombre y correo.

---

## C-01 — Carrito en sesión

**Fase 1 · Rama:** `claudio/c-01-carrito`

**Objetivo:** el carrito de compras, guardado en la sesión del navegador (sin tablas).

**Qué debe quedar hecho**
1. **Agregar** (`cart:agregar`, POST): recibe `variante_id` y `cantidad`. Si la variante ya estaba, **suma** la cantidad. Luego redirige al carrito con un mensaje de éxito.
2. **Página del carrito** (`cart:ver`): una tabla con producto, variante, precio unitario, cantidad y subtotal de cada línea. Abajo, el subtotal general. El precio se lee de la base de datos usando `precio_final`.
3. **Actualizar cantidad** (`cart:actualizar`, POST): cada línea tiene su control de cantidad. Si la cantidad llega a 0, la línea se elimina.
4. **Eliminar** (`cart:eliminar`, POST): quita una línea.
5. **Validaciones**, cada una con su mensaje de error:
   - la cantidad debe ser un número entero mayor que cero;
   - no se puede pedir más de lo que hay en inventario;
   - la variante debe existir y su producto estar activo.
6. **Carrito vacío:** un mensaje y un enlace para volver a la tienda. Sin tabla vacía.
7. El **número de artículos** del carrito se ve en el menú de todas las páginas. Para eso necesitas un "procesador de contexto"; tú lo escribes y Vicente lo registra en `settings.py`.
8. Toda la lógica del carrito (agregar, quitar, calcular totales) vive en **un solo lugar** dentro de `apps/cart/`, no repetida en cada vista. El plan `C-03` la va a reutilizar.

La estructura exacta que se guarda en la sesión está en `ACUERDOS.md`, sección 6. Respétala.

**Cómo se comprueba**
- [ ] Agregar dos veces la misma variante deja una sola línea con la cantidad sumada.
- [ ] Los subtotales y el total son correctos, incluso con productos en oferta.
- [ ] Pedir más del inventario disponible muestra error y no cambia el carrito.
- [ ] Enviar una cantidad con letras o negativa muestra error, no una página 500.
- [ ] Abrir el sitio en una ventana de incógnito muestra un carrito **vacío** (es otro comprador).
- [ ] Cerrar la pestaña y volver a abrirla conserva el carrito.
- [ ] Si un producto del carrito se desactiva en el admin, el carrito no se rompe.
- [ ] Todas las acciones que cambian el carrito son POST con CSRF.

**Conceptos que debes dominar:** qué es una sesión y dónde la guarda Django, cómo leer y escribir en `request.session` (y por qué a veces hay que avisar que cambió), datos de un POST, redirecciones, sistema de mensajes, procesadores de contexto.

**Commits sugeridos:** agregar al carrito → página con tabla y totales → actualizar cantidad → eliminar → validaciones → contador en el menú.

---

## C-02 — Cupones

**Fase 1 · Rama:** `claudio/c-02-cupones`

**Objetivo:** aplicar códigos de descuento en el carrito.

**Qué debe quedar hecho**
1. En `apps/promotions/`, **una función** que recibe un código y el subtotal, y responde si el cupón es válido, cuánto descuenta y, si no es válido, el motivo. Esta función es la única que decide; el carrito y el checkout la llaman.
2. Un cupón es válido solo si **todo** se cumple:
   - existe (sin importar mayúsculas o minúsculas ni espacios al escribirlo);
   - está activo;
   - la fecha de hoy está entre `valido_desde` y `valido_hasta`;
   - el subtotal es igual o mayor que `total_minimo`.
3. Cálculo del descuento:
   - `PORCENTAJE`: ese porcentaje del subtotal;
   - `FIJO`: ese monto.
   - El descuento **nunca** es mayor que el subtotal (el total no baja de cero).
4. En la página del carrito: una caja para escribir el código (`cart:aplicar_cupon`, campo `codigo`) y un botón para quitarlo (`cart:quitar_cupon`).
5. El carrito muestra subtotal, descuento y total.
6. Cada motivo de rechazo tiene **su propio mensaje** ("el cupón venció", "compra mínima de X", etc.).
7. El cupón se **vuelve a validar** cada vez que se muestra el carrito. Si el comprador quita productos y ya no llega al mínimo, el cupón se retira solo y se le avisa.

**Cómo se comprueba**
- [ ] Un cupón de porcentaje y uno fijo de los datos de ejemplo calculan bien.
- [ ] Un cupón vencido, uno inactivo y uno inexistente se rechazan, cada uno con su mensaje.
- [ ] Escribir el código en minúsculas funciona.
- [ ] Un cupón fijo mayor que el subtotal deja el total en 0, no en negativo.
- [ ] Aplicar un cupón con mínimo, y luego bajar cantidades por debajo del mínimo, retira el cupón.
- [ ] La validación está en `apps/promotions/`, no copiada dentro de las vistas.

**Conceptos que debes dominar:** fechas con zona horaria en Django (`timezone`), números decimales para dinero (`Decimal`, nunca `float`), separar lógica de negocio de las vistas.

**Commits sugeridos:** función de validación → cálculo del descuento → aplicar en carrito → quitar cupón → revalidación automática.

---

## C-03 — Checkout y orden

**Fase 2 · Rama:** `claudio/c-03-checkout`

**Objetivo:** convertir el carrito en una orden real en la base de datos.

**Qué debe quedar hecho**
1. **Página de checkout** (`orders:checkout`): resumen del pedido (líneas, subtotal, descuento, total) y el formulario de envío.
2. **Formulario** hecho con Django Forms, con `nombre_envio`, `direccion_envio` y `telefono`. HTML **semántico**: cada campo con su etiqueta, tipos de campo correctos, campos obligatorios marcados. Los errores se muestran junto al campo que falló.
3. Validación del teléfono: solo dígitos, espacios y guiones, con un largo razonable.
4. Al confirmar (POST), y **antes de guardar nada**, se revisa de nuevo: carrito no vacío, inventario suficiente de cada línea y cupón todavía válido. Si algo falla, se regresa al carrito con el mensaje.
5. Si todo está bien se crea:
   - la `Orden` con `clave_sesion`, datos de envío, `subtotal`, `descuento`, `total`, `cupon` y estado `READY_TO_SHIP`;
   - un `ItemOrden` por cada línea, con `precio_unitario` copiado del precio actual y su `total_linea`.
6. **Todo o nada:** si falla la creación de una línea, no queda una orden a medias.
7. Después de crear la orden: el carrito y el cupón se **borran de la sesión** y se redirige a la confirmación.
8. **Página de confirmación** (`orders:confirmacion`): número de orden, resumen y mensaje de éxito. Solo la puede ver la sesión que hizo la compra; para cualquier otra, 404.
9. Entrar al checkout con el carrito vacío redirige a la tienda con un aviso.

**Ojo:** un visitante nuevo puede no tener clave de sesión todavía. Investiga cómo asegurarte de que exista antes de guardarla en la orden.

**Cómo se comprueba**
- [ ] Una compra completa crea una `Orden` y sus `ItemOrden` con totales correctos (se ve en el admin).
- [ ] La orden nueva aparece en el almacén (`/almacen/`).
- [ ] Enviar el formulario vacío muestra los errores en cada campo y **no** crea orden.
- [ ] Tras comprar, el carrito queda vacío y recargar la confirmación no crea otra orden.
- [ ] Cambiar el precio del producto en el admin después de comprar no cambia la orden.
- [ ] Abrir la confirmación de esa orden en incógnito da 404.
- [ ] Si el inventario bajó mientras el comprador llenaba el formulario, no se crea la orden y se le avisa.
- [ ] El inventario **no** baja al comprar (baja al despachar, plan `F-03`).

**Conceptos que debes dominar:** Django Forms y validación de campos, crear objetos relacionados con el ORM, transacciones (`transaction.atomic`), patrón POST → redirección → GET.

**Commits sugeridos:** formulario y página → validaciones del formulario → creación de orden y líneas → limpieza de sesión y confirmación → revalidación de inventario y cupón.

---

## C-04 — Prueba del flujo completo y video demo

**Fase 3 · Rama:** `claudio/c-04-pruebas-demo`

**Objetivo:** demostrar que todo funciona de punta a punta y dejar la evidencia que pide el profesor.

**Qué debe quedar hecho**
1. Un archivo `docs/PRUEBAS.md` (este sí lo creas tú) con una tabla: caso, pasos, resultado esperado, resultado obtenido. Mínimo estos casos:
   - compra completa sin cupón;
   - compra con cupón de porcentaje y con cupón fijo;
   - cupón inválido;
   - intento de comprar más del inventario;
   - dos compradores a la vez (ventana normal e incógnito) con carritos separados;
   - despacho correcto y despacho bloqueado por inventario.
2. Cada fallo encontrado se reporta como **Issue** en GitHub asignado al dueño de la app. No lo arregles tú si no es tu app.
3. Un texto de 5 a 8 líneas para el README explicando **cómo se manejan las sesiones** y cómo simular otro comprador (ventana de incógnito o borrar las cookies). Se lo entregas a Vicente en el PR.
4. **Video demo** de 3 a 5 minutos recorriendo: tienda → producto → carrito → cupón → checkout → almacén → despacho. El enlace va en el PR.

**Cómo se comprueba**
- [ ] `docs/PRUEBAS.md` tiene todos los casos con su resultado.
- [ ] Los fallos están como Issues, con pasos para repetirlos.
- [ ] El video muestra el flujo completo sin cortes en los pasos importantes.
- [ ] El texto de sesiones está en la descripción del PR.
