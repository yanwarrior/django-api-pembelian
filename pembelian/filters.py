import django_filters

from pembelian.models import Pembelian, Item


class PembelianFilter(django_filters.FilterSet):
    class Meta:
        model = Pembelian
        fields = {
            'nomor': ['exact'],
            'supplier__nama': ['contains'],
            'supplier__telepon': ['contains'],
            'supplier__pic': ['contains']
        }


class ItemFilter(django_filters.FilterSet):
    class Meta:
        model = Item
        fields = {
            'barang': ['exact'],
            'pembelian': ['exact']
        }