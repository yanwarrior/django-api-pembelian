import django_filters

from stok.models import Stok


class StokFilter(django_filters.FilterSet):
    class Meta:
        model = Stok
        fields = {
            'nomor_transaksi': ['exact'],
            'nomor': ['exact'],
            'barang__nomor': ['contains']
        }