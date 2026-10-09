from django.urls import path

from config.views import en_construccion

from . import views

# Agrupar los nombres de las rutas bajo catalog.
app_name = 'catalog'

# Conectar inicio y categorías con sus vistas; búsqueda y producto siguen pendientes.
urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('categoria/<slug:slug>/', views.categoria, name='categoria'),
    path('buscar/', en_construccion, name='buscar'),
    path('producto/<slug:slug>/', en_construccion, name='producto'),
]
