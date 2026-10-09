from decimal import Decimal

from apps.catalog.models import Variante


class ErrorCarrito(ValueError):
    pass


def _guardar(session, carrito):
    session['carrito'] = carrito
    session.modified = True


def _obtener_id_variante(valor):
    try:
        variante_id = int(valor)
    except (TypeError, ValueError):
        raise ErrorCarrito('La variante elegida no es válida.') from None
    if variante_id <= 0:
        raise ErrorCarrito('La variante elegida no es válida.')
    return variante_id


def _obtener_cantidad(valor):
    try:
        cantidad = int(valor)
    except (TypeError, ValueError):
        raise ErrorCarrito('La cantidad debe ser un número entero mayor que cero.') from None
    return cantidad


def _obtener_variante_activa(variante_id):
    try:
        variante = Variante.objects.select_related('producto').get(pk=variante_id)
    except Variante.DoesNotExist:
        raise ErrorCarrito('La variante seleccionada no existe.') from None

    if not variante.producto.activo:
        raise ErrorCarrito('Este producto ya no está disponible.')
    return variante


def _carrito_de_sesion(session):
    carrito = session.get('carrito', {})
    if isinstance(carrito, dict):
        return carrito
    _guardar(session, {})
    return {}


def agregar_variante(session, variante_id, cantidad):
    variante_id = _obtener_id_variante(variante_id)
    cantidad = _obtener_cantidad(cantidad)
    if cantidad <= 0:
        raise ErrorCarrito('La cantidad debe ser un número entero mayor que cero.')

    variante = _obtener_variante_activa(variante_id)
    carrito = _carrito_de_sesion(session).copy()
    clave = str(variante_id)
    try:
        cantidad_actual = int(carrito.get(clave, 0))
    except (TypeError, ValueError):
        cantidad_actual = 0
    if cantidad_actual < 0:
        cantidad_actual = 0

    nueva_cantidad = cantidad_actual + cantidad
    disponible = variante.cantidad_disponible
    if nueva_cantidad > disponible:
        raise ErrorCarrito(
            f'No hay suficiente inventario para {variante.producto.nombre}. '
            f'Disponible: {disponible}.'
        )

    carrito[clave] = nueva_cantidad
    _guardar(session, carrito)
    return variante.producto.nombre


def actualizar_variante(session, variante_id, cantidad):
    variante_id = _obtener_id_variante(variante_id)
    cantidad = _obtener_cantidad(cantidad)
    carrito = _carrito_de_sesion(session).copy()
    clave = str(variante_id)

    if cantidad == 0:
        carrito.pop(clave, None)
        _guardar(session, carrito)
        return False
    if cantidad < 0:
        raise ErrorCarrito('La cantidad debe ser un número entero mayor que cero.')

    variante = _obtener_variante_activa(variante_id)
    disponible = variante.cantidad_disponible
    if cantidad > disponible:
        raise ErrorCarrito(
            f'No hay suficiente inventario para {variante.producto.nombre}. '
            f'Disponible: {disponible}.'
        )

    carrito[clave] = cantidad
    _guardar(session, carrito)
    return True


def eliminar_variante(session, variante_id):
    variante_id = _obtener_id_variante(variante_id)
    carrito = _carrito_de_sesion(session).copy()
    carrito.pop(str(variante_id), None)
    _guardar(session, carrito)


def obtener_resumen(session):
    carrito_original = _carrito_de_sesion(session)
    carrito = carrito_original.copy()
    lineas = []
    subtotal = Decimal('0')

    for variante_id, cantidad in carrito_original.items():
        try:
            variante_id_int = int(variante_id)
            cantidad_int = int(cantidad)
        except (TypeError, ValueError):
            carrito.pop(variante_id, None)
            continue

        if variante_id_int <= 0:
            carrito.pop(variante_id, None)
            continue

        try:
            variante = Variante.objects.select_related('producto').get(pk=variante_id_int)
        except Variante.DoesNotExist:
            carrito.pop(variante_id, None)
            continue
        if cantidad_int <= 0 or not variante.producto.activo:
            carrito.pop(variante_id, None)
            continue

        precio_unitario = variante.producto.precio_final
        total_linea = precio_unitario * cantidad_int
        subtotal += total_linea
        lineas.append({
            'variante': variante,
            'cantidad': cantidad_int,
            'precio_unitario': precio_unitario,
            'subtotal': total_linea,
        })

    if carrito != carrito_original:
        _guardar(session, carrito)
    return lineas, subtotal


def contar_articulos(session):
    carrito = _carrito_de_sesion(session)
    total = 0
    for cantidad in carrito.values():
        try:
            cantidad_int = int(cantidad)
        except (TypeError, ValueError):
            continue
        if cantidad_int > 0:
            total += cantidad_int
    return total
