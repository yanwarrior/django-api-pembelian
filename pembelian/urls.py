from django.urls import path

from pembelian.views import pembelian_list

app_name = 'pembelian'

urlpatterns = [
    path('', pembelian_list, name='pembelian-list'),
]