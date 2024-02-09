from django.urls import path

from pembelian.views import pembelian_list, pembelian_detail, pembelian_publish, pembayaran_detail, item_list, \
    item_detail, hutang_detail, retur_list, retur_detail, retur_published, retur_item_list, retur_item_detail, \
    pembelian_choice

app_name = 'pembelian'

urlpatterns = [
    path('', pembelian_list, name='pembelian-list'),
    path('<int:pk>/', pembelian_detail, name='pembelian-detail'),
    path('<str:nomor>/choice/', pembelian_choice, name='pembelian-choice'),
    path('<int:pk>/publish/', pembelian_publish, name='pembelian-publish'),
    path('<int:pk>/pembayaran/', pembayaran_detail, name='pembayaran-detail'),
    path('<int:pk>/items/', item_list, name='item-list'),
    path('<int:pk>/items/<int:item_pk>/', item_detail, name='item-detail'),
    path('<int:id>/hutang/', hutang_detail, name='hutang-detail'),
    path('<int:id>/retur/', retur_list, name='retur-list'),
    path('<int:id>/retur/<int:retur_id>/', retur_detail, name='retur-detail'),
    path('<int:id>/retur/<int:retur_id>/published/', retur_published, name='retur-published'),
    path('<int:id>/retur/<int:retur_id>/items/', retur_item_list, name='retur-item-list'),
    path('<int:id>/retur/<int:retur_id>/items/<int:item_id>/', retur_item_detail, name='retur-item-detail'),
]
