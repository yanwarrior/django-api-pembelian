from django.urls import path

from pembelian.views import pembelian_list, pembelian_detail, pembayaran_detail, item_list

app_name = 'pembelian'

urlpatterns = [
    path('', pembelian_list, name='pembelian-list'),
    path('<int:pk>/', pembelian_detail, name='pembelian-detail'),
    path('<int:pk>/pembayaran/', pembayaran_detail, name='pembayaran-detail'),
    path('<int:pk>/items/', item_list, name='item-list'),
]