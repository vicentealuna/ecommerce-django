from django.urls import path

from config.views import en_construccion

app_name = 'catalog'

urlpatterns = [
    path('', en_construccion, name='inicio'),
    path('categoria/<slug:slug>/', en_construccion, name='categoria'),
    path('buscar/', en_construccion, name='buscar'),
    path('producto/<slug:slug>/', en_construccion, name='producto'),
]
