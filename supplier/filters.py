import django_filters
from django.db.models import Q

from supplier.models import Supplier


class SupplierFilter(django_filters.FilterSet):
    class Meta:
        model = Supplier
        fields = {
            "nomor": ['exact'],
            'nama': ['contains'],
            "telepon": ['exact'],
            "bank": ['exact'],
            "contact_person": ['contains']
        }


class SupplierSearch:
    @staticmethod
    def query(request):
        search = request.GET.get('search', '')
        return Q(nomor__contains=search) \
               | Q(nama__contains=search) \
               | Q(telepon__contains=search) \
               | Q(bank__contains=search) \
               | Q(contact_person__contains=search)
