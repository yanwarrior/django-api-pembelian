import django_filters
from django.db.models import Q

from pembelian.models import Pembelian, Item, Hutang, ReturPembelian, ReturItemPembelian


class PembelianFilter(django_filters.FilterSet):
    class Meta:
        model = Pembelian
        fields = {
            'nomor': ['exact'],
            'is_draft': ['exact'],
            'pembayaran_pembelian__lunas': ['exact'],
            'supplier__nama': ['icontains', 'exact'],
            'supplier__telepon': ['contains', 'exact'],
            'supplier__contact_person': ['contains', 'exact']
        }

class PembelianSearch:
    @staticmethod
    def query(request):
        return Q(supplier__nama__contains=request.GET.get('search', '')) \
               | Q(nomor__contains=request.GET.get('search', '')) \
               | Q(supplier__nomor__contains=request.GET.get('search', ''))



class ItemFilter(django_filters.FilterSet):
    class Meta:
        model = Item
        fields = {
            'barang__nomor': ['exact'],
            'barang__nama': ['exact'],
        }


class HutangFilter(django_filters.FilterSet):
    class Meta:
        model = Hutang
        fields = {

            'sisa': ['contains'],
        }


class ReturPembelianFilter(django_filters.FilterSet):
    class Meta:
        model = ReturPembelian
        fields = {
            'nomor': ['exact'],
            'pembelian__nomor': ['exact'],
            'pembelian__supplier__nomor': ['exact'],
        }


class ReturItemPembelianFilter(django_filters.FilterSet):
    class Meta:
        model = ReturItemPembelian
        fields = {
            'barang__nama': ['contains'],
        }


