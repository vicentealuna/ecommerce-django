from django.urls import path

from apps.orders.views import checkout, confirmacion

app_name = 'orders'

urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('orden/<int:orden_id>/confirmada/', confirmacion, name='confirmacion'),
]
