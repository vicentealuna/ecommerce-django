from django.urls import path

from config.views import en_construccion

app_name = 'warehouse'

urlpatterns = [
    path('', en_construccion, name='lista'),
    path('orden/<int:orden_id>/', en_construccion, name='detalle'),
    path('orden/<int:orden_id>/despachar/', en_construccion, name='despachar'),
]
