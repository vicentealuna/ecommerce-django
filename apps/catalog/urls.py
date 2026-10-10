from django.urls import path

from . import views

# Agrupar los nombres de las rutas bajo catalog.
app_name = 'catalog'

# Conectar las páginas del catálogo con sus vistas.
urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('categoria/<slug:slug>/', views.categoria, name='categoria'),
    path('buscar/', views.buscar, name='buscar'),
    path('producto/<slug:slug>/', views.producto, name='producto'),
]
