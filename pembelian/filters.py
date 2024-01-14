import django_filters

from pembelian.models import Pembelian, Item, Hutang


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


class HutangFilter(django_filters.FilterSet):
    class Meta:
        model = Hutang
        fields = {
            'nomor': ['contains'],
            'jumlah': ['contains'],
            'sisa': ['contains'],
        }