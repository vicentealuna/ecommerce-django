# Pruebas de aceptación del flujo de compra

## Entorno y alcance

Las pruebas se ejecutaron en un worktree aislado con C-03 ya integrado en
`main` y el candidato de F-03 del PR #11 (`9efa95b90362650c200ce4aa8b5a59e1beb95936`).
F-03 todavía estaba en revisión; por eso estos resultados no afirman que el
almacén ya esté integrado en `main`. Se cargó `base_de_datos/datos_iniciales.json`
en la base local aislada. Las ocho filas se verificaron con clientes Django
separados y transacciones revertidas para conservar intactos los datos de ejemplo.

| Caso | Pasos | Resultado esperado | Resultado obtenido |
|---|---|---|---|
| Compra completa sin cupón | Agregar una camiseta al carrito; confirmar el checkout con datos de envío. | Se crea una orden `READY_TO_SHIP`, con sus líneas y el total correcto; comprar no descuenta inventario. | **Aprobado.** Orden creada por $650.00; el inventario permaneció igual. |
| Compra con cupón de porcentaje | Agregar una camiseta y aplicar `BIENVENIDO10`; confirmar la compra. | El cupón queda asociado a la orden y descuenta el 10 % del subtotal. | **Aprobado.** Descuento de $65.00; total de $585.00. |
| Compra con cupón fijo | Agregar una camiseta y aplicar `AHORRA200`; confirmar la compra. | El cupón queda asociado a la orden y resta $200.00 del subtotal. | **Aprobado.** Descuento de $200.00; total de $450.00. |
| Cupón inválido | Agregar una camiseta e intentar aplicar `VENCIDO15`. | El cupón se rechaza y no queda guardado en la sesión. | **Aprobado.** El cupón vencido fue rechazado y la sesión no conservó el código. |
| Intento de comprar más del inventario | Consultar las 3 unidades de la mochila; intentar agregar 4 al carrito. | La cantidad se rechaza, se avisa al comprador y el carrito no cambia. | **Aprobado.** Se rechazó agregar más de las existencias y el carrito quedó intacto. |
| Dos compradores a la vez | En dos clientes/sesiones independientes, agregar variantes diferentes y comparar sus carritos. | Cada comprador ve solo los artículos guardados en su propia sesión. | **Aprobado.** Las sesiones conservaron carritos distintos (`{"1": 2}` y `{"2": 3}`). |
| Despacho correcto | Crear una orden con inventario suficiente y enviarla a despachar desde el almacén. | La orden pasa a `DESPATCHED`, se descuenta el stock y se registran el despacho y el movimiento de salida. | **Aprobado.** Se comprobaron el cambio de estado, el descuento y ambos registros asociados. |
| Despacho bloqueado por inventario | Abrir la orden de ejemplo #3, que solicita 5 mochilas cuando hay 3, e intentar despacharla. | Se informa que no alcanza el inventario; la orden sigue pendiente y no se altera el stock ni se registra el despacho. | **Aprobado.** Se informó el inventario insuficiente y no hubo cambios de estado, stock o despacho. |

## Validaciones automatizadas

- `python manage.py test` (en el worktree aislado de C-03 + F-03): **72 pruebas, OK**.
- `python manage.py migrate`: **OK**.
- `python manage.py loaddata base_de_datos/datos_iniciales.json`: **98 objetos cargados, OK**.
- `python manage.py check`: **sin problemas**.

No se encontró un fallo reproducible durante estas pruebas, así que no se abrió
ningún Issue. La demostración del flujo completo se hace en local, siguiendo el
recorrido de la sección "Demo" del README.
