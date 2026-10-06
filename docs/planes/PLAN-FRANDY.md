# PLAN DE FRANDY

Tus planes: `F-00` → `F-01` → `F-02` → `F-03` → `F-04`. Hazlos en ese orden, uno por rama.

Tus archivos: `apps/catalog/` y `apps/warehouse/` (vistas, urls y plantillas) y `static/css/estilos.css`.
**No tocas:** ningún `models.py`, `admin.py`, `migrations/`, `config/`, `templates/base.html`, ni las apps de Claudio.

Antes de empezar lee [`ACUERDOS.md`](../ACUERDOS.md) y [`GUIA-GIT.md`](../GUIA-GIT.md).

Este plan dice **qué** debe quedar funcionando, no trae el código. Investígalo por tu cuenta o con tu IA, pero pégale primero `ACUERDOS.md`. Al final debes poder explicar cada línea que subas: Vicente puede preguntártelo en la revisión.

---

## F-00 — Incorporación

**Fase 0 · Rama:** `frandy/f-00-incorporacion`

**Objetivo:** tener el proyecto funcionando en tu equipo y practicar el ciclo completo de git con algo que no puede romper nada.

**Qué hacer**
1. Sigue la sección 1 de `GUIA-GIT.md` hasta ver la tienda en tu navegador.
2. Entra a `/admin/` con el superusuario que creaste y mira los productos, variantes e inventario de ejemplo. Entiende cómo se relacionan. Lee también las tablas "Cómo ir de un modelo a otro" y "Datos de ejemplo" de `ACUERDOS.md`.
3. Crea tu rama, y en el archivo `EQUIPO.md` agrega una línea con tu nombre y tus apps.
4. Commit, push y abre el PR.

**Cómo se comprueba**
- [ ] Existe un PR titulado `F-00 Incorporación` desde la rama correcta.
- [ ] El PR solo cambia `EQUIPO.md`.
- [ ] El commit sale con tu nombre y correo.

---

## F-01 — Tienda

**Fase 1 · Rama:** `frandy/f-01-tienda`

**Objetivo:** la página de inicio donde el comprador descubre los productos.

**Qué debe quedar hecho**
1. **Inicio** (`catalog:inicio`): una sección de productos **destacados** y otra de productos **en oferta**. En los de oferta se ve el precio normal tachado y el precio de oferta.
2. **Menú de categorías** visible en la tienda. Al elegir una, se listan sus productos (`catalog:categoria`). Si la categoría tiene subcategorías, también se muestran los productos de esas.
3. **Búsqueda simple** (`catalog:buscar`): una caja de texto que busca en el nombre y la descripción. Si no hay resultados, lo dice con un mensaje claro.
4. Cada producto se muestra como una **tarjeta**: imagen principal, nombre, precio y enlace a su página. Haz la tarjeta en un archivo aparte y reutilízala en inicio, categoría y búsqueda.
5. Solo aparecen productos **activos**.

**Cómo se comprueba**
- [ ] `/` muestra las dos secciones con los productos de ejemplo.
- [ ] Al desactivar un producto en el admin, desaparece de inicio, categoría y búsqueda.
- [ ] Al marcar un producto como destacado en el admin, aparece en destacados.
- [ ] Una categoría que no existe da página 404, no error 500.
- [ ] Buscar una palabra que no existe muestra "sin resultados", no una página vacía.
- [ ] Un producto sin imagen no rompe la tarjeta.
- [ ] En celular las tarjetas se acomodan en una o dos columnas.

**Conceptos que debes dominar:** consultas con filtros del ORM, búsqueda con varias condiciones (objetos `Q`), `get_object_or_404`, herencia de plantillas, `include` de plantillas, rejilla de Bootstrap.

**Commits sugeridos:** inicio con destacados → sección de ofertas → tarjeta reutilizable → categorías → búsqueda → ajustes responsive.

---

## F-02 — Página de producto

**Fase 1 · Rama:** `frandy/f-02-producto`

**Objetivo:** la página donde el comprador decide y agrega al carrito.

**Qué debe quedar hecho**
1. Página (`catalog:producto`) con nombre, descripción completa, precio (y oferta si aplica) y categoría con enlace.
2. **Todas las imágenes** del producto, cada una con su texto alternativo.
3. **Selector de variante** con las variantes del producto. Cada opción indica si está agotada; las agotadas no se pueden elegir.
4. **Selector de cantidad**, mínimo 1.
5. Botón **Agregar al carrito**: un formulario que envía por POST a `cart:agregar` los campos `variante_id` y `cantidad`. Los nombres de los campos están en `ACUERDOS.md` y deben ser exactos, porque del otro lado los recibe Claudio.
6. Si **todas** las variantes están agotadas, se muestra "Agotado" y no hay botón.

**Cómo se comprueba**
- [ ] Un producto con varias variantes las muestra todas en el selector.
- [ ] Un producto con una sola variante `Única` funciona igual.
- [ ] Poner el inventario de una variante en 0 desde el admin la muestra como agotada.
- [ ] Un producto inactivo o inexistente da 404.
- [ ] El formulario lleva token CSRF y usa los nombres `variante_id` y `cantidad`.
- [ ] Con el plan `C-01` de Claudio ya unido: al pulsar el botón, el producto aparece en el carrito.

**Nota:** mientras Claudio no termine `C-01`, el botón te llevará a una página "En construcción". Es lo esperado. Tu parte se revisa mirando que el formulario envíe los datos correctos.

**Conceptos que debes dominar:** relaciones inversas del ORM (de producto a sus imágenes y variantes), formularios HTML con POST y CSRF, etiqueta `url` en plantillas.

**Commits sugeridos:** detalle básico → galería de imágenes → selector de variantes → control de agotados → formulario de agregar.

---

## F-03 — Almacén

**Fase 2 · Rama:** `frandy/f-03-almacen`

**Objetivo:** el área donde se preparan y despachan las órdenes. Es la **lógica más delicada** del proyecto: aquí se mueve el inventario.

**Qué debe quedar hecho**
1. **Lista** (`warehouse:lista`): órdenes en estado `READY_TO_SHIP`, de la más antigua a la más nueva, con número, fecha, nombre de envío y cantidad de artículos.
2. **Detalle** (`warehouse:detalle`): datos de envío y la tabla de productos con variante, cantidad pedida y **cuánto hay en inventario**. Si de algún producto no alcanza, se resalta.
3. Botón **Despachar** (`warehouse:despachar`, solo POST). Al pulsarlo, por cada línea de la orden:
   - se registra un `MovimientoInventario` de tipo `SALIDA` con la orden relacionada;
   - se resta la cantidad del `ItemStock`.

   Y además se crea el `Despacho` y la orden pasa a `DESPATCHED`.
4. **Todo o nada:** si a una sola línea le falta inventario, **no se despacha nada**, no se guarda ningún movimiento y se muestra un mensaje de error diciendo qué producto falta.
5. Una orden ya despachada **no se puede despachar otra vez**, aunque alguien recargue o repita el envío.
6. Mensaje de éxito al despachar y regreso a la lista.

**Cómo se comprueba**
- [ ] La lista muestra las órdenes de ejemplo y no muestra las ya despachadas.
- [ ] Al despachar: el inventario baja lo correcto, hay un movimiento `SALIDA` por línea, existe el `Despacho` y la orden queda `DESPATCHED` (se verifica en el admin).
- [ ] Con inventario insuficiente: aparece el error y **nada** cambió en la base de datos.
- [ ] Entrar a `despachar` escribiendo la dirección en el navegador (GET) no despacha.
- [ ] Repetir el despacho de la misma orden no descuenta inventario dos veces.
- [ ] El inventario nunca queda en negativo.

**Para probar sin esperar a Claudio:** los datos iniciales traen órdenes de ejemplo en `READY_TO_SHIP`. Si las gastas, vuelve a cargar el fixture.

**Conceptos que debes dominar:** transacciones de base de datos en Django (`transaction.atomic`) y por qué hacen falta aquí, restringir una vista a POST, actualizar y guardar objetos con el ORM, sistema de mensajes.

**Commits sugeridos:** lista → detalle con inventario → despacho feliz → bloqueo por falta de inventario → bloqueo de doble despacho.

---

## F-04 — Pulido visual y responsive

**Fase 3 · Rama:** `frandy/f-04-pulido-visual`

**Objetivo:** que todo el sitio se vea como **un solo** proyecto y funcione en celular. El profesor valora la creatividad en el diseño.

En este plan sí puedes tocar las plantillas de Claudio, pero **solo clases y estructura visual**, no la lógica ni los nombres de campos. Avísale antes.

**Qué debe quedar hecho**
1. Revisar todas las páginas (inicio, categoría, búsqueda, producto, carrito, checkout, confirmación, almacén lista y detalle) en ancho de celular, tableta y escritorio.
2. Mismos colores, tipografía, botones y espaciados en todas. Lo propio va en `static/css/estilos.css`.
3. Las tablas (carrito, almacén) no se salen de la pantalla en celular.
4. Proponer a Vicente los ajustes de `base.html` (menú, pie de página). Él los aplica.
5. Toda imagen tiene texto alternativo y todo campo de formulario tiene su etiqueta.

**Cómo se comprueba**
- [ ] Ninguna página tiene barra de desplazamiento horizontal a 375 px de ancho.
- [ ] El PR incluye capturas de cada página en celular y en escritorio.
- [ ] No cambió ningún `name` de formulario ni ningún archivo `.py`.
