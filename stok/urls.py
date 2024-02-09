from django.urls import path

from stok.views import stok_list

app_name = 'stok'

urlpatterns = [
    path('', stok_list, name='stok-list'),
]