import django_filters

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