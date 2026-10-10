from django.urls import path

from config.views import en_construccion

from . import views

# Agrupar los nombres de las rutas bajo catalog.
app_name = 'catalog'

# Conectar inicio, categorías y búsqueda; el detalle de producto sigue pendiente.
urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('categoria/<slug:slug>/', views.categoria, name='categoria'),
    path('buscar/', views.buscar, name='buscar'),
    path('producto/<slug:slug>/', en_construccion, name='producto'),
]
