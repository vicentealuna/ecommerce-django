from apps.accounts.roles import rol_de


def rol_context(request):
    # El menú de base.html muestra el rol junto al nombre del usuario.
    return {'rol_usuario': rol_de(request.user)}
