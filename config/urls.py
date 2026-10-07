"""
Rutas principales del proyecto.

Cada app tiene su propio urls.py. La tabla completa de rutas y sus nombres
está en docs/ACUERDOS.md, sección 7.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('carrito/', include('apps.cart.urls')),
    path('almacen/', include('apps.warehouse.urls')),
    path('', include('apps.orders.urls')),
    path('', include('apps.catalog.urls')),
]

# En desarrollo, Django sirve las imágenes de media/
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
