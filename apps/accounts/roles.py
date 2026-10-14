"""
Roles del sitio.

- Administrador: usuario con acceso al admin de Django (is_staff).
- Almacén: usuario que pertenece al grupo "Almacén".
- Cliente: cualquier otro usuario registrado. Al registrarse entra al grupo "Cliente".

Los grupos se crean con la migración de esta app y se asignan desde el admin.
Los roles no bloquean ninguna página: la tienda y el almacén siguen abiertos.
"""

GRUPO_CLIENTE = 'Cliente'
GRUPO_ALMACEN = 'Almacén'

ROL_ADMINISTRADOR = 'Administrador'
ROL_ALMACEN = 'Almacén'
ROL_CLIENTE = 'Cliente'


def rol_de(usuario):
    """Devuelve el nombre del rol del usuario, o un texto vacío si no inició sesión."""
    if not usuario.is_authenticated:
        return ''
    if usuario.is_staff:
        return ROL_ADMINISTRADOR
    if usuario.groups.filter(name=GRUPO_ALMACEN).exists():
        return ROL_ALMACEN
    return ROL_CLIENTE
