from django.urls import path

from barang.views import barang_list, barang_detail, barang_number

app_name = "barang"

urlpatterns = [
    path('', barang_list, name='barang-list'),
    path('number/', barang_number, name='barang-number'),
    path('<int:id>/', barang_detail, name='barang-detail'),
]