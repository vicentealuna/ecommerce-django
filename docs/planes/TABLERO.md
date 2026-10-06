# TABLERO DEL PROYECTO

Vista general: qué hay que hacer, quién lo hace y en qué orden. Vicente actualiza la columna **Estado**.

Antes de empezar, lee en este orden:

1. [`ACUERDOS.md`](../ACUERDOS.md) — nombres, carpetas y rutas que todos respetamos.
2. [`GUIA-GIT.md`](../GUIA-GIT.md) — cómo crear tu rama, hacer commit y subir.
3. Tu plan: [Vicente](PLAN-VICENTE.md) · [Frandy](PLAN-FRANDY.md) · [Claudio](PLAN-CLAUDIO.md)

---

## Calendario

Entrega al profesor: **lunes 19 de octubre de 2026**. Son 13 días desde el arranque, así que no hay margen para atrasos largos.

| Fase | Fechas | Días |
|------|--------|------|
| 0 — Cimientos | martes 6 al jueves 8 de octubre | 3 |
| 1 — Tienda y carrito | viernes 9 al martes 13 de octubre | 5 |
| 2 — Compra y almacén | miércoles 14 al viernes 16 de octubre | 3 |
| 3 — Cierre y entrega | sábado 17 y domingo 18 de octubre | 2 |
| Entrega | lunes 19 de octubre | — |

El último día de cada fase es para **tener los PR unidos**, no para abrirlos. Abre tu PR al menos un día antes, para que haya tiempo de revisar y corregir.

Si terminas un plan antes de su fecha, empieza el siguiente. No esperes.

---

## Fases

Estados posibles: `Pendiente` · `En curso` · `En revisión` (PR abierto) · `Hecho` (unido a `main`) · `Devuelto` (hay que corregir).

### Fase 0 — Cimientos

Vicente deja el proyecto listo para que los demás solo tengan que programar su parte. Frandy y Claudio se instalan y practican el flujo de git con un PR de prueba.

| Código | Plan | Responsable | Depende de | Estado |
|--------|------|-------------|------------|--------|
| `V-00` | Repositorio y carpeta compartida | Vicente | — | Pendiente |
| `V-01` | Esqueleto del proyecto | Vicente | V-00 | Pendiente |
| `V-02` | Modelos, admin y datos iniciales | Vicente | V-01 | Pendiente |
| `F-00` | Incorporación | Frandy | V-02 | Pendiente |
| `C-00` | Incorporación | Claudio | V-02 | Pendiente |

**La fase termina cuando:** los tres tienen el proyecto corriendo en su equipo con los mismos productos de ejemplo, y Frandy y Claudio ya unieron su PR de prueba.

### Fase 1 — Tienda y carrito

Frandy y Claudio trabajan en paralelo, sin esperarse.

| Código | Plan | Responsable | Depende de | Estado |
|--------|------|-------------|------------|--------|
| `F-01` | Tienda (inicio, categorías, búsqueda) | Frandy | F-00 | Pendiente |
| `F-02` | Página de producto | Frandy | F-01 | Pendiente |
| `C-01` | Carrito en sesión | Claudio | C-00 | Pendiente |
| `C-02` | Cupones | Claudio | C-01 | Pendiente |

**La fase termina cuando:** se puede entrar a la tienda, abrir un producto, agregarlo al carrito, cambiar cantidades y aplicar un cupón.

### Fase 2 — Compra y almacén

| Código | Plan | Responsable | Depende de | Estado |
|--------|------|-------------|------------|--------|
| `C-03` | Checkout y orden | Claudio | C-02 | Pendiente |
| `F-03` | Almacén | Frandy | F-00 (usa órdenes de ejemplo) | Pendiente |

**La fase termina cuando:** una compra hecha en la tienda aparece en el almacén y se puede despachar.

### Fase 3 — Cierre y entrega

| Código | Plan | Responsable | Depende de | Estado |
|--------|------|-------------|------------|--------|
| `F-04` | Pulido visual y responsive | Frandy | Fase 2 | Pendiente |
| `C-04` | Prueba del flujo completo y video demo | Claudio | Fase 2 | Pendiente |
| `V-03` | README, fixtures finales y entrega | Vicente | F-04, C-04 | Pendiente |

**La fase termina cuando:** alguien que nunca vio el proyecto puede clonarlo, seguir el README y hacer una compra completa.

---

## Reparto de la carga

| Persona | Planes | Parte visual (plantillas) | Parte lógica (vistas, ORM) | Peso aprox. |
|---------|--------|---------------------------|----------------------------|-------------|
| Frandy | F-00 a F-04 | Tienda, producto, almacén, pulido | Búsqueda y filtros, **despacho con inventario** | 40 % |
| Claudio | C-00 a C-04 | **Carrito, formulario de checkout, confirmación** | Sesión, cupones, creación de orden | 40 % |
| Vicente | V-00 a V-03 | Plantilla base | Modelos y admin | 20 % + revisar y unir todos los PR |

Frandy no hace solo pantallas y Claudio no hace solo lógica: cada uno entrega funciones completas, de la base de datos a la página. A Frandy le toca la lógica más delicada del proyecto (despachar) y a Claudio dos de las páginas con más formulario (carrito y checkout).

---

## Qué plan cubre cada punto de la nota (40 pts)

| Criterio del profesor | Planes |
|-----------------------|--------|
| Diseño y responsividad | V-01, F-04 (y cada plan con página) |
| Catálogo y detalle de producto | V-02, F-01, F-02 |
| Carrito (agregar/actualizar/eliminar) + cupones | C-01, C-02 |
| Checkout y creación de órdenes | C-03 |
| Almacén (listar, detalle, despachar) | F-03 |
| Calidad del código y documentación | Todos + V-03 |
| Repositorio con commits significativos | Todos (ver GUIA-GIT) |
| README con instrucciones y decisiones | V-03 |
| Carpeta `base_de_datos/` con fixtures | V-02, V-03 |
| Demo local o video | C-04 |

---

## Cómo se da por terminado un plan

Un plan pasa a `Hecho` solo si cumple **todo** esto:

1. Está en una rama con el nombre correcto y el PR lleva el código del plan en el título.
2. Cumple **todos** los puntos de "Cómo se comprueba" de su plan.
3. No toca archivos de otro dueño.
4. `python manage.py check` no muestra errores y el servidor arranca.
5. Tiene varios commits con mensajes claros, no uno solo.

Si falta algo, el PR se **devuelve** con una nota de qué falta. Vicente no corrige el trabajo de otro: lo corrige su autor.
