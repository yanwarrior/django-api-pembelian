import django_filters as filters
from django.db.models import Q

from barang.models import Barang


class BarangFilter(filters.FilterSet):
    class Meta:
        model = Barang
        fields = {
            'nomor': ['exact'],
            'nama': ['exact', 'contains'],
        }
class BarangSearch:
    @staticmethod
    def query(request):
        return Q(nama__contains=request.GET.get('search', '')) \
                | Q(nomor__contains=request.GET.get('search', '')) \
                | Q(satuan__contains=request.GET.get('search', ''))
