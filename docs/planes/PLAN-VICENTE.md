# PLAN DE VICENTE

Tus planes: `V-00` → `V-01` → `V-02` → (revisar PR durante Fases 1 y 2) → `V-03`.

Tu trabajo tiene dos partes:

1. **Construir los cimientos** (Fase 0): repositorio, esqueleto y modelos. Mientras no termines, Frandy y Claudio no pueden empezar. Es tu prioridad número uno.
2. **Cuidar `main`** (Fases 1 a 3): revisar y unir los Pull Requests.

Tus archivos: `config/`, `templates/base.html`, todos los `models.py`, `admin.py` y `migrations/`, `requirements.txt`, `.gitignore`, `docs/`, `base_de_datos/`.

---

## V-00 — Repositorio y carpeta compartida

**Fase 0 · Sin rama (es el único trabajo que va directo a `main`)**

**Objetivo:** que exista el repositorio en GitHub, con los planes dentro, y que los tres tengan acceso.

### Paso 1. Convertir esta carpeta en repositorio

La carpeta `Proyectos_Django/ecommerce-django/` ya tiene la carpeta `docs/` con los planes. Abre una terminal **dentro de ella**:

```bash
git init -b main
```

Crea a mano dos archivos antes del primer commit:

- `.gitignore` con estas líneas: `.venv/`, `__pycache__/`, `*.pyc`, `db.sqlite3`, `.env`, `.vscode/`, `.idea/`.
- `EQUIPO.md` con un título y tu nombre con tus responsabilidades. Frandy y Claudio agregarán su línea en su PR de prueba.

```bash
git add .
```

```bash
git status
```

```bash
git commit -m "V-00: documentos del equipo y planes de trabajo"
```

### Paso 2. Crear el repositorio en GitHub

1. En github.com: botón **+** → **New repository**.
2. Nombre: `ecommerce-django`.
3. Visibilidad: **Public** (recomendado). El profesor podrá verlo sin invitación y, sobre todo, GitHub solo permite proteger la rama `main` gratis en repositorios públicos.
4. **No** marques "Add a README", ni `.gitignore`, ni licencia. El repositorio debe nacer vacío, porque ya tienes contenido local.
5. **Create repository** y copia la dirección que te muestra.

Conecta tu carpeta con GitHub y sube:

```bash
git remote add origin https://github.com/TU-USUARIO/ecommerce-django.git
```

```bash
git push -u origin main
```

### Paso 3. Dar acceso a Frandy y Claudio

**Settings → Collaborators → Add people.** Escribe el usuario de GitHub de cada uno. Ellos deben **aceptar la invitación** que les llega al correo; hasta entonces no pueden subir nada.

### Paso 4. Proteger `main`

**Settings → Branches → Add branch ruleset** (o "Add classic branch protection rule"):

- Rama: `main`.
- Marca **Require a pull request before merging**.
- Marca **Require approvals: 1**.
- Marca **Block force pushes**.
- Marca **Require status checks to pass** y agrega la revisión `revisar` (del flujo **Sin marca de agua**). Solo aparece en la lista después de que se haya ejecutado al menos una vez.

Con esto nadie puede subir directo a `main`: todo pasa por un PR que tú apruebas. Ojo: esa regla también te aplica a ti, así que desde `V-01` tú también trabajas en ramas. Como eres el único revisor, en tus propios PR usa la opción de administrador para unirlos (o pide a un compañero que apruebe; es buena práctica).

En **Settings → General → Pull Requests** deja marcado **Allow merge commits** y desmarca *squash* y *rebase*. El "squash" aplasta todos los commits en uno, y el profesor califica "commits significativos" de cada integrante.

### Paso 5. La carpeta compartida de planes

**No hace falta Drive ni mandar archivos por WhatsApp.** La carpeta compartida es `docs/` dentro del mismo repositorio. Hay una sola copia y siempre es la última.

Envía este mensaje al grupo (cambia la dirección):

> Muchachos, el repositorio del proyecto es: `https://github.com/TU-USUARIO/ecommerce-django`
>
> 1. Acepten la invitación que les llegó al correo de GitHub.
> 2. Los planes están en la carpeta **docs**. Se leen directo en la página de GitHub, no hay que descargar nada.
> 3. Lean en este orden: `docs/ACUERDOS.md`, `docs/GUIA-GIT.md` y su plan en `docs/planes/`.
> 4. El tablero general está en `docs/planes/TABLERO.md`. Ahí se ve en qué va cada uno.
> 5. Cuando yo cambie un plan les aviso por aquí. Para ver el cambio: recarguen la página de GitHub, o en su computadora hagan `git switch main` y `git pull origin main`.
> 6. La carpeta `docs` solo la edito yo. Si algo de su plan no se entiende o creen que está mal, me escriben.
> 7. Antes de usar su IA, péguenle `ACUERDOS.md` completo.

**Cómo actualizar un plan después:** edita el archivo en una rama `vicente/docs-...`, PR, merge y avisa. También puedes editarlo desde la página de GitHub con el ícono del lápiz; GitHub te crea la rama y el PR.

**Truco para ver qué cambió en un plan:** en GitHub, abre el archivo y pulsa **History**. Ahí queda cada versión con su fecha.

**Cómo se comprueba**
- [ ] El repositorio existe y es visible con `docs/` dentro.
- [ ] Frandy y Claudio aparecen como colaboradores (invitación aceptada).
- [ ] Intentar `git push` directo a `main` es rechazado.
- [ ] Solo está permitido "merge commit".
- [ ] La revisión **Sin marca de agua** aparece en verde en la pestaña Actions y es obligatoria para unir.

---

## V-01 — Esqueleto del proyecto

**Fase 0 · Rama:** `vicente/v-01-esqueleto`

**Objetivo:** un proyecto Django que arranca, con todas las apps, todas las rutas y la plantilla base. Los demás solo rellenan.

**Qué debe quedar hecho**
1. Entorno virtual, Django 5.2 y Pillow instalados, y `requirements.txt` con las versiones fijas.
2. Proyecto creado con `django-admin startproject config .` (el punto final lo crea en la carpeta actual, sin subcarpeta extra).
3. Las cinco apps dentro de `apps/`: `catalog`, `cart`, `promotions`, `orders`, `warehouse`. Cada una registrada en `INSTALLED_APPS`.
   - Ojo: al estar dentro de `apps/`, en el `apps.py` de cada una el `name` debe ser `apps.catalog`, `apps.cart`, etc. Si no, Django no las encuentra. Es el error más común de esta estructura.
4. `settings.py`: idioma español, zona horaria `America/Santo_Domingo`, carpeta `templates/` general, `static/` y `media/` configurados.
5. `config/urls.py` incluye el `urls.py` de cada app y sirve los archivos de `media/` en modo desarrollo.
6. Cada app tiene su `urls.py` con su `app_name` y **todas** las rutas de la tabla de `ACUERDOS.md`, sección 7, apuntando a una vista provisional que muestra "En construcción". Así ningún enlace entre páginas falla mientras el compañero termina.
7. `templates/base.html` con: Bootstrap 5 por CDN, enlace a `static/css/estilos.css`, menú (Tienda, Carrito, Almacén), zona donde se muestran los **mensajes de Django**, bloque de contenido y pie de página.
8. Carpetas vacías `base_de_datos/` y `media/` presentes en el repositorio (git no guarda carpetas vacías: ponles un archivo `.gitkeep`).
9. La plantilla de Pull Request ya está en `.github/pull_request_template.md`; verifica que aparezca al abrir tu PR.

**Cómo se comprueba**
- [ ] `python manage.py check` no reporta errores.
- [ ] `python manage.py runserver` arranca y **cada** ruta de la tabla responde "En construcción" con el menú de `base.html`.
- [ ] `/admin/` muestra la pantalla de ingreso.
- [ ] `git status` no lista `db.sqlite3` ni `.venv/`.

**Commits sugeridos:** proyecto y requirements → apps registradas → settings (idioma, static, media, templates) → rutas provisionales → base.html.

---

## V-02 — Modelos, admin y datos iniciales

**Fase 0 · Rama:** `vicente/v-02-modelos`

**Objetivo:** la base de datos completa y datos de ejemplo iguales para los tres. Tú escribes **todos** los modelos porque son el contrato: si cada uno escribe los suyos con su IA, no encajan, y las migraciones chocan.

**Qué debe quedar hecho**
1. Los 10 modelos de `ACUERDOS.md`, sección 6, con esos nombres exactos de modelo y de campo.
2. Detalles que no pueden faltar:
   - dinero con campos decimales, nunca flotantes;
   - `slug` único en Categoria y Producto;
   - `estado`, `tipo` y `tipo_descuento` con opciones fijas (`choices`);
   - cantidades que no admitan negativos;
   - una sola fila de `ItemStock` por variante y un solo `Despacho` por orden;
   - Producto con la propiedad `precio_final`;
   - que no se pueda borrar una variante o producto que ya está en una orden (protegido, no en cascada);
   - cada modelo con su `__str__` legible.
3. Migraciones creadas y aplicadas.
4. **Admin** con todos los modelos registrados. En Producto, las imágenes y las variantes se editan en la misma pantalla (busca "inlines"). El `slug` se llena solo a partir del nombre.
5. Superusuario creado en tu equipo con `createsuperuser`. Los usuarios no viajan en el repositorio: cada compañero crea el suyo.
6. **Datos de ejemplo** cargados desde el admin:
   - 3 categorías, una con una subcategoría;
   - 8 a 10 productos: algunos destacados, algunos en oferta, uno inactivo, uno con varias variantes, uno con variante `Única`, uno con una variante en inventario 0;
   - imágenes de ejemplo (libres de derechos y livianas);
   - 4 cupones: uno de porcentaje, uno fijo, uno vencido, uno con compra mínima;
   - 3 órdenes en `READY_TO_SHIP` con sus líneas, una de ellas pidiendo más de lo que hay en inventario. Las necesita Frandy para probar el almacén sin esperar a Claudio.
7. Fixture exportado a `base_de_datos/datos_iniciales.json` y las imágenes de `media/` subidas al repositorio.

Exporta así. Usa `-o` y no el símbolo `>`: en PowerShell el `>` guarda el archivo con una codificación que luego `loaddata` no puede leer.

```bash
python -Xutf8 manage.py dumpdata catalog promotions orders warehouse --indent 2 -o base_de_datos/datos_iniciales.json
```

**Cómo se comprueba**
- [ ] Borrando `db.sqlite3`, y corriendo `migrate` y luego `loaddata base_de_datos/datos_iniciales.json`, aparecen todos los datos con sus imágenes.
- [ ] Los nombres de modelos y campos coinciden letra por letra con `ACUERDOS.md`.
- [ ] En el admin se puede crear un producto con sus imágenes y variantes en una sola pantalla.
- [ ] `python manage.py makemigrations --check` dice que no hay cambios pendientes.

**Al terminar:** avisa al grupo que pueden empezar `F-00` y `C-00`, y actualiza el tablero.

**Commits sugeridos:** modelos de catalog → promotions → orders → warehouse → admin → fixture e imágenes.

---

## Tu rol durante las Fases 1 y 2: revisar y unir

### Cómo revisar un Pull Request

1. **Lee la descripción.** Si la plantilla está vacía, devuélvelo sin revisar más.
2. **Mira "Files changed" en GitHub.** Preguntas rápidas:
   - ¿Tocó archivos que no son suyos? (ver tabla de dueños)
   - ¿Hay migraciones, `db.sqlite3` o librerías nuevas? Eso es devolución inmediata.
   - ¿La revisión **Sin marca de agua** está en verde? Si está en rojo, no se une.
   - ¿Los nombres coinciden con `ACUERDOS.md`?
3. **Pruébalo en tu equipo:**

```bash
git fetch origin
```

```bash
git switch frandy/f-01-tienda
```

```bash
python manage.py migrate
```

```bash
python manage.py runserver
```

4. **Recorre la lista "Cómo se comprueba"** del plan, punto por punto. Esa lista es tu criterio; no apruebes por "se ve bien".
5. **Decide en GitHub** (botón *Review changes*):
   - **Approve** → luego **Merge pull request** (merge commit) y borra la rama con el botón que aparece.
   - **Request changes** → escribe qué punto de la lista falla y cómo lo viste fallar. El autor corrige en la misma rama.
6. Vuelve a `main`, actualiza, cambia el estado en `TABLERO.md` y avisa al grupo que hay cambios nuevos.

```bash
git switch main
```

```bash
git pull origin main
```

### Reglas para ti como revisor

- **No corrijas el código de otro.** Si lo arreglas tú, él no aprende y tú cargas con su trabajo. Devuélvelo con una nota clara.
- **Revisa en menos de 24 horas.** Un PR esperando es un compañero detenido.
- **Une los PR de uno en uno** y prueba `main` después de cada uno. Si unes tres de golpe y algo falla, no sabrás cuál fue.
- **Pregunta "¿por qué lo hiciste así?"** en una o dos líneas de cada PR. Si no sabe responder, lo copió sin entender: que lo estudie y lo explique antes de unir.
- **Cuando te pidan un cambio en modelos o en `base.html`:** hazlo tú en una rama `vicente/...` corta, únelo rápido y avisa para que actualicen.

### Si alguien se atrasa o entrega mal

1. Primera devolución: nota clara con los puntos que fallan.
2. Segunda devolución del mismo plan: llamada de 15 minutos para ver qué no entiende.
3. Si a mitad de la fase un plan no ha arrancado: se reasigna por su código. Los planes son independientes justamente para esto.

Puedes pedirme en cualquier momento: *"revisa el repositorio y dime si F-01 cumple su plan"*. Yo comparo la rama contra la lista "Cómo se comprueba".

---

## V-03 — README, fixtures finales y entrega

**Fase 3 · Rama:** `vicente/v-03-entrega`

**Objetivo:** dejar el repositorio listo para que el profesor lo clone y lo califique.

**Qué debe quedar hecho**
1. **README.md** con:
   - qué es el proyecto y quiénes lo hicieron;
   - requisitos e instrucciones paso a paso para correrlo (clonar, entorno, instalar, migrar, cargar fixtures, arrancar);
   - cómo entrar al admin;
   - mapa de páginas con sus rutas;
   - **cómo se manejan las sesiones** y cómo simular otro comprador (texto que entrega Claudio en `C-04`);
   - **decisiones técnicas**: la tabla D1–D11 de `ACUERDOS.md`, con su porqué;
   - enlace al video demo;
   - qué hizo cada integrante.
2. **Fixtures finales** en `base_de_datos/`, exportados de nuevo con los datos definitivos.
3. Verificación de entrega **en una carpeta nueva**, como lo hará el profesor: clonar, seguir el README al pie de la letra y hacer una compra completa hasta despacharla.
4. Todos los Issues abiertos por Claudio en `C-04` cerrados o explicados.
5. `TABLERO.md` con todo en `Hecho`.

**Cómo se comprueba**
- [ ] Un clon limpio funciona siguiendo solo el README.
- [ ] `base_de_datos/` tiene fixtures que cargan sin error.
- [ ] El README explica sesiones y decisiones técnicas.
- [ ] El historial muestra commits de los tres integrantes con mensajes claros.
