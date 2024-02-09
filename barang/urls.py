from django.urls import path

from barang.views import barang_list, barang_detail, barang_choice

app_name = "barang"

urlpatterns = [
    path('', barang_list, name='barang-list'),
    path('<int:id>/', barang_detail, name='barang-detail'),
    path('<str:nomor>/choice/', barang_choice, name='barang-choice'),
]