# GUÍA DE GIT DEL EQUIPO

Comandos para Windows (PowerShell). Se escriben dentro de la carpeta del proyecto.

## Idea general

- `main` es la versión buena del proyecto. **Nadie programa en `main`.**
- Cada plan (`F-01`, `C-02`...) se hace en **su propia rama**.
- Cuando el plan está terminado, se abre un **Pull Request (PR)**. Vicente lo revisa y lo une a `main`.

```
main ──●────────────●───────────●──→
        \          / \         /
         F-01 ──●─●   C-01 ─●─●
```

---

## 1. La primera vez (una sola vez por persona)

Identifícate, para que tus commits salgan a tu nombre. Usa el mismo correo de tu cuenta de GitHub:

```bash
git config --global user.name "Tu Nombre"
```

```bash
git config --global user.email "tu-correo@ejemplo.com"
```

Descarga el proyecto (Vicente te pasa la dirección):

```bash
git clone https://github.com/USUARIO/ecommerce-django.git
```

```bash
cd ecommerce-django
```

Activa el filtro de marcas de agua (sección 10). Se hace una sola vez:

```bash
git config core.hooksPath .githooks
```

Prepara tu entorno:

```bash
python -m venv .venv
```

```bash
.venv\Scripts\Activate.ps1
```

```bash
pip install -r requirements.txt
```

```bash
python manage.py migrate
```

```bash
python manage.py loaddata base_de_datos/datos_iniciales.json
```

```bash
python manage.py runserver
```

Si `Activate.ps1` da error de permisos, abre la terminal **cmd** en vez de PowerShell y usa `.venv\Scripts\activate.bat`.

Cada vez que abras una terminal nueva hay que activar el entorno otra vez. Sabes que está activo porque la línea empieza con `(.venv)`.

---

## 2. Empezar un plan

**Dónde se crea la rama:** siempre desde `main` **recién actualizado**. Nunca desde otra rama tuya ni de un compañero.

```bash
git switch main
```

```bash
git pull origin main
```

```bash
git switch -c frandy/f-01-tienda
```

**Nombre de la rama:** `tunombre/codigo-del-plan-descripcion`, todo en minúsculas. Ejemplos: `claudio/c-01-carrito`, `frandy/f-03-almacen`, `vicente/v-02-modelos`.

Una rama = un plan. No mezcles dos planes en una rama.

Si `main` trajo migraciones o datos nuevos, actualiza tu base de datos:

```bash
python manage.py migrate
```

---

## 3. Mientras trabajas: commits

Mira qué cambiaste:

```bash
git status
```

Agrega **solo** los archivos que tocaste a propósito (revisa la lista antes):

```bash
git add apps/catalog/views.py apps/catalog/templates/catalog/inicio.html
```

Guarda el commit, empezando por el código del plan:

```bash
git commit -m "F-01: muestra productos destacados en el inicio"
```

### Cuándo hacer commit

| Sí, haz commit cuando... | No hagas commit cuando... |
|--------------------------|---------------------------|
| Terminaste **una cosa pequeña que funciona** (una vista, una plantilla, una validación). | El servidor no arranca o la página da error. |
| Vas a intentar algo arriesgado: guarda antes lo que ya sirve. | Solo llevas código a medias que rompe lo anterior. |
| Vas a cerrar la computadora y lo que hay funciona. | Hay archivos que no reconoces en `git status`. |

Antes de cada commit, comprueba que nada esté roto:

```bash
python manage.py check
```

Lo normal son **entre 4 y 10 commits por plan**. Un solo commit gigante con "todo listo" no cuenta como "commits significativos" para el profesor, y es casi imposible de revisar.

### Cómo escribir el mensaje

`CÓDIGO: qué hace ahora el proyecto que antes no hacía`

- Bien: `C-01: permite eliminar un producto del carrito`
- Bien: `F-03: bloquea el despacho si no hay inventario suficiente`
- Mal: `cambios`, `avance`, `arreglos varios`, `listo`

---

## 4. Subir tu rama: push

La primera vez que subes una rama:

```bash
git push -u origin frandy/f-01-tienda
```

Las siguientes veces:

```bash
git push
```

### Cuándo hacer push

- **Al terminar cada sesión de trabajo**, aunque el plan no esté completo. Tu rama es tuya; subirla no afecta a nadie y sirve de respaldo.
- **Antes de pedir ayuda**, para que el compañero pueda ver tu código.
- **Antes de abrir el Pull Request.**

Commit guarda en tu computadora. Push lo manda a GitHub. Si no hay push, nadie más lo ve y, si se daña tu equipo, se pierde.

---

## 5. Ponerte al día con `main`

Hazlo cuando Vicente avise que unió algo nuevo, y **siempre antes de abrir tu PR**:

```bash
git switch main
```

```bash
git pull origin main
```

```bash
git switch frandy/f-01-tienda
```

```bash
git merge main
```

```bash
python manage.py migrate
```

### Si aparece un conflicto

Git te dirá qué archivos chocan. Ábrelos: verás marcas `<<<<<<<`, `=======` y `>>>>>>>`. Arriba está tu versión, abajo la de `main`. Deja el código como debe quedar, borra las marcas, y luego:

```bash
git add nombre-del-archivo
```

```bash
git commit -m "F-01: resuelve conflicto con main"
```

Si no entiendes el conflicto, **no adivines**. Cancela y pregunta a Vicente:

```bash
git merge --abort
```

Si respetaste la tabla de dueños de `ACUERDOS.md`, casi nunca habrá conflictos.

---

## 6. Abrir el Pull Request

1. Haz push de tu rama.
2. Entra al repositorio en GitHub. Aparece un botón **Compare & pull request**.
3. Verifica: **base: `main`** ← **compare: tu rama**.
4. Título: código y nombre del plan. Ejemplo: `F-01 Tienda`.
5. Llena la plantilla que aparece (qué hiciste, cómo probarlo, capturas).
6. A la derecha, en **Reviewers**, elige a Vicente.
7. Avisa en el grupo.

Si Vicente pide cambios: hazlos **en la misma rama**, commit y push. El PR se actualiza solo. No abras otro PR.

Cuando Vicente lo una, limpia tu equipo:

```bash
git switch main
```

```bash
git pull origin main
```

```bash
git branch -d frandy/f-01-tienda
```

---

## 7. Lo que NO se hace

| Nunca | Por qué |
|-------|---------|
| Programar o hacer commit directamente en `main` | `main` debe funcionar siempre. |
| `git push --force` | Borra trabajo de otros sin aviso. |
| `git add .` sin mirar `git status` antes | Subes archivos que no debías (base de datos, migraciones, basura). |
| Subir `db.sqlite3` o `.venv/` | Cada quien tiene los suyos. Los datos se comparten con fixtures. |
| Editar archivos de otro dueño | Es la causa número uno de conflictos. |
| Unir (merge) tu propio PR | Lo une Vicente después de revisarlo. |
| Borrar la carpeta y clonar de nuevo "para arreglar" | Pierdes lo que no habías subido. Pregunta primero. |

---

## 8. Comandos de consulta (no cambian nada)

| Comando | Para qué |
|---------|----------|
| `git status` | Ver en qué rama estás y qué cambiaste. |
| `git branch` | Ver tus ramas. La actual tiene un `*`. |
| `git log --oneline -10` | Ver los últimos 10 commits. |
| `git diff` | Ver línea por línea lo que cambiaste y aún no guardaste. |

## 9. Deshacer sin romper

Descartar los cambios de un archivo que aún no tiene commit (se pierden esos cambios):

```bash
git restore nombre-del-archivo
```

Sacar un archivo que agregaste por error con `git add` (no pierdes nada):

```bash
git restore --staged nombre-del-archivo
```

Corregir el mensaje del último commit, **solo si aún no hiciste push**:

```bash
git commit --amend -m "F-01: mensaje corregido"
```

Para cualquier otra cosa que quieras deshacer, pregunta antes.

---

## 10. Cero marcas de agua de IA

Muchas herramientas de IA firman solas lo que hacen: agregan al mensaje del commit una línea de co-autor con su nombre, o dejan comentarios en el código diciendo que ellas lo generaron. En este proyecto eso **no se permite**: los commits salen solo a tu nombre.

Hay dos filtros:

| Filtro | Dónde actúa | Qué hace |
|--------|-------------|----------|
| Hook local | En tu computadora, al hacer `git commit` | Rechaza el commit en el momento y te dice qué línea sobra. |
| Revisión **Sin marca de agua** | En GitHub, en cada Pull Request | Revisa todos los commits y archivos nuevos del PR. Si falla, el PR no se puede unir. |

El hook local solo funciona si lo activaste (sección 1). Compruébalo así; debe responder `.githooks`:

```bash
git config core.hooksPath
```

### Cómo evitarlo

- En la configuración de tu herramienta de IA busca la opción de **co-autor** o **atribución** en commits y apágala.
- Mejor aún: escribe tú el mensaje del commit y haz tú el `git commit`. Así además sabes qué estás subiendo.
- Antes de hacer commit, lee el código que te dio la IA y borra comentarios que la mencionen.

### Si el hook rechazó tu commit

No se guardó nada. Repite el commit con un mensaje limpio:

```bash
git commit -m "F-01: mensaje sin firma de IA"
```

### Si la revisión de GitHub falló

Abre la pestaña **Checks** del PR: te dice qué commit o qué línea tiene la marca.

- **La marca está en un archivo:** bórrala, haz commit y push. La revisión se repite sola.
- **La marca está en tu último commit:** corrige el mensaje y vuelve a subir. Este es el **único** caso en que se permite forzar, y solo en **tu propia rama**:

```bash
git commit --amend -m "F-01: mensaje sin firma de IA"
```

```bash
git push --force-with-lease
```

- **La marca está en un commit más viejo:** no intentes arreglarlo solo. Escribe a Vicente.

