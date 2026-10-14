from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.accounts.forms import IngresoForm, RegistroForm
from apps.accounts.roles import GRUPO_CLIENTE

# Lo que el comprador ya tenía en la sesión y debe conservar al cerrar sesión.
CLAVES_DEL_CARRITO = ['carrito', 'cupon_codigo']


def destino_seguro(request):
    """Devuelve la página a la que se quería ir, solo si pertenece a este sitio."""
    destino = request.POST.get('next') or request.GET.get('next') or ''
    if url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
        return destino
    return ''


def registro(request):
    if request.user.is_authenticated:
        return redirect('catalog:inicio')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            # Todo usuario nuevo entra con el rol de cliente.
            grupo, _ = Group.objects.get_or_create(name=GRUPO_CLIENTE)
            usuario.groups.add(grupo)
            # Iniciar sesión conserva el carrito que ya tenía como visitante.
            login(request, usuario)
            messages.success(request, f'Cuenta creada. Bienvenido, {usuario.username}.')
            return redirect(destino_seguro(request) or 'catalog:inicio')
    else:
        form = RegistroForm()

    return render(request, 'accounts/registro.html', {
        'form': form,
        'next': destino_seguro(request),
    })


def ingresar(request):
    if request.user.is_authenticated:
        return redirect('catalog:inicio')

    if request.method == 'POST':
        form = IngresoForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            messages.success(request, f'Hola de nuevo, {usuario.username}.')
            return redirect(destino_seguro(request) or 'catalog:inicio')
    else:
        form = IngresoForm(request)

    return render(request, 'accounts/ingresar.html', {
        'form': form,
        'next': destino_seguro(request),
    })


@require_POST
def salir(request):
    # Cerrar sesión borra la sesión completa: se guarda el carrito y se devuelve después.
    guardado = {
        clave: request.session[clave]
        for clave in CLAVES_DEL_CARRITO
        if clave in request.session
    }
    logout(request)
    for clave, valor in guardado.items():
        request.session[clave] = valor
    messages.info(request, 'Cerraste sesión.')
    return redirect('catalog:inicio')
