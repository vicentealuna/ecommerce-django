from django.shortcuts import render


def en_construccion(request, **kwargs):
    """Vista provisional. Cada dueño la reemplaza por la vista real de su ruta."""
    return render(request, 'en_construccion.html', {
        'ruta': request.resolver_match.view_name,
    })
