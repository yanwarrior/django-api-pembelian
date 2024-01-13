import django_filters as filters

from barang.models import Barang


class BarangFilter(filters.FilterSet):
    class Meta:
        model = Barang
        fields = {
            'nomor': ['exact'],
            'nama': ['contains'],
            'merek': ['contains'],
        }
