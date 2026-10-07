from django.urls import path

from config.views import en_construccion

app_name = 'orders'

urlpatterns = [
    path('checkout/', en_construccion, name='checkout'),
    path('orden/<int:orden_id>/confirmada/', en_construccion, name='confirmacion'),
]
